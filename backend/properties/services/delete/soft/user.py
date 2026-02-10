from __future__ import annotations
from typing import TYPE_CHECKING, List, Type

if TYPE_CHECKING:
    from properties.models import User, Booking, LandlordProfile, DeletionLog, Review, CompanyMembership

import logging

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from properties.models import User, Booking
from properties.services.delete.soft.base import BaseCascadeDelete
from properties.services.delete.class_mixin.booking import BookingCheckMixin
from properties.services.delete.email.soft_admin import SoftAdminResponse
from properties.services.delete.email.soft_user import SoftUserResponse
from properties.utils.decorators import atomic_handel

logger = logging.getLogger(__name__)


class UserCascadeDelete(BaseCascadeDelete, BookingCheckMixin):
    """
    Concrete implementation of `BaseCascadeDelete` for handling user deletions.

    Supports:
        - Soft deletion of the user.
        - Cascade deletion of related models:
            - Reviews authored by the user.
            - Landlord profiles (individual or company) and associated properties/memberships.
        - Active booking checks before deletion.
        - Logging deletion events using `CreateLogModel`.
        - Notifications on success, failure, or errors.

    Attributes:
        is_landlord (bool): True if the user is a landlord.
        landlord_profile (IndividualLandlord | List[Company] | None): Landlord profile(s) of the user.
    """

    def __init__(self, target_model: User, deleted_by: User, reason: str,
                 email_handler: Type[SoftAdminResponse | SoftUserResponse]) -> None:
        super().__init__(target_model, deleted_by, reason, email_handler)
        self.is_landlord: bool = target_model.is_landlord
        self.landlord_profile: LandlordProfile | List[LandlordProfile] | None = self._manage_if_landlord()

    @classmethod
    def create(cls, target_model: User, deleted_by: User, reason: str) -> UserCascadeDelete:
        """
        Factory method to create a UserCascadeDelete handler.

        Decides whether to use `SoftAdminResponse` or `SoftUserResponse`
        based on the executor and deletion reason.

        Args:
            target_model (User): User instance to delete.
            deleted_by (User): User performing the deletion.
            reason (str): Reason for deletion.

        Returns:
            UserCascadeDelete: Instance of this deletion handler.

        Raises:
            ValidationError: If the account is already deleted.
            PermissionDenied: If the user lacks permissions.
        """
        if target_model.is_deleted:
            raise ValidationError({'detail': _('Account data is already deleted.')})
        email_handler: Type[SoftAdminResponse | SoftUserResponse] = cls._prevalidate(target_model, deleted_by, reason)

        return cls(target_model, deleted_by, reason, email_handler)

    def _manage_if_landlord(self):
        """
        Determine and retrieve landlord profile(s) if the user is a landlord.

        Returns:
            LandlordProfile | List[LandlordProfile] | None:
                - Landlord profile(s) if the user has landlord status
                  and a valid landlord type (individual or company).
                - None if the user is not a landlord or has no valid type.
        """
        if self.is_landlord and self.target_model.landlord_type in [self._INDIVIDUAL, self._COMPANY]:
            return self._get_landlord_profile()
        return None

    def _handle_reviews(self, parent_log: DeletionLog) -> None:
        """
        Log all reviews authored by the user before soft deletion.

        Args:
            parent_log (DeletionLog): Parent deletion log entry to attach review logs to.
        """
        reviews_list: List[Review] = list(Review.objects.not_deleted(author=self.target_model))

        if reviews_list:
            self.log_model.list_handler(reviews_list, parent_log)

    def _handle_company_membership(self, parent_log: DeletionLog):
        """
        Logs all user membership models before soft deletion.

        Args:
            parent_log (DeletionLog): Parent deletion log entry to attach company membership logs to.
        """
        membership_list: List[CompanyMembership] = CompanyMembership.objects.filter(user=self.target_model)

        if membership_list:
            self.log_model.list_handler(membership_list, parent_log)

    def _check_active_bookings(self) -> List[Booking]:
        """
        Aggregate all active bookings related to the user that would prevent deletion.

        This includes:
            1. Bookings where the user is a guest.
            2. Bookings for properties owned by the user's landlord profile(s),
               whether individual or company.

        Returns:
            List[Booking]: All active Booking instances preventing deletion.
        """
        active_bookings: List[Booking] = self._get_active_bookings()

        if self.is_landlord and self.landlord_profile is not None:
            properties_bookings: List[Booking] = self._get_active_property_list_booking()

            if properties_bookings:
                active_bookings.extend(properties_bookings)

        return active_bookings

    @atomic_handel
    def _delete(self) -> None:
        """
        Perform the cascade deletion of the user and related models.

        Steps:
            1. Create deletion log for the user.
            2. Delete reviews authored by the user.
            3. Delete landlord profile(s) and associated properties/memberships.
            4. Soft-delete the user account itself.

        Notes:
            - All database operations are executed within an atomic transaction.
            - Any exception raised here will propagate to `execute()` for handling.
        """
        parent_log: DeletionLog = self.log_model.user_log(self.target_model, self.reason)

        self._handle_reviews(parent_log)

        if self.is_landlord and self.target_model.landlord_type == self._COMPANY_MEMBER:
            self._handle_company_membership(parent_log)

        elif self.is_landlord and self.landlord_profile is not None:
            if isinstance(self.landlord_profile, list):
                self.log_model.landlord_profile_list(self.landlord_profile, parent_log)
            else:
                self.log_model.landlord_profile(self.landlord_profile, parent_log)

        self.target_model.soft_delete()

    def execute(self) -> None:
        """
        Execute the deletion workflow for the user.

        Steps:
            1. Check for active bookings.
            2. Notify if deletion cannot proceed due to active bookings.
            3. Perform deletion via `_delete`.
            4. Send success notifications.
            5. Log and handle any unexpected errors.

        Exceptions are caught and handled via `self.email_handler.handle_error`.
        """
        try:
            has_active_bookings: List[Booking] = self._check_active_bookings()

            if has_active_bookings:
                landlord: bool = True if self.is_landlord and self.landlord_profile is not None else False
                self.email_handler.handle_failed(has_active_bookings, landlord)
                return

            self._delete()

            self.email_handler.handle_success()
        except Exception as e:
            logger.exception(f'Failed to soft delete user {self.target_model.pk}: {e}')
            self.email_handler.handle_error()

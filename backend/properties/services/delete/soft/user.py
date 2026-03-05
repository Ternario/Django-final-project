from __future__ import annotations
from typing import List, Type

from properties.utils.choices.review import ReviewStatus

import logging

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from properties.models import User, Booking, DeletionLog, Review, LandlordProfile
from properties.services.delete.soft.base import BaseCascadeDelete
from properties.services.delete.class_mixin.cascade_actions_mixin import CascadeActionsMixin
from properties.services.delete.email.soft_admin import SoftAdminResponse
from properties.services.delete.email.soft_user import SoftUserResponse
from properties.utils.decorators import atomic_handel

logger = logging.getLogger(__name__)


class UserCascadeDelete(BaseCascadeDelete, CascadeActionsMixin):
    """
    Concrete implementation of `BaseCascadeDelete` for handling user soft deletions.

    Supports:
        - Soft deletion of the user account.
        - Cascade handling of related models:
            - Reviews authored by the user.
            - Landlord profiles (individual or company) and associated properties/memberships.
        - Checks for active bookings before deletion and prevents deletion if any exist.
        - Logging deletion events using `CreateLogModel`.
        - Notifications on deletion success, failure, or unexpected errors.

    Attributes:
        is_landlord (bool): True if the user has a landlord role.
        landlord_type (str): Type of landlord relationship (individual, company, company member).
        landlord_profile (List[LandlordProfile] | None): Landlord profile(s) of the user, if applicable.
    """

    def __init__(self, target_model: User, deleted_by: User, reason: str | None,
                 email_handler: Type[SoftAdminResponse | SoftUserResponse]) -> None:
        super().__init__(target_model, deleted_by, reason, email_handler)
        self.is_landlord: bool = target_model.is_landlord
        self.landlord_type: str = target_model.landlord_type
        self.landlord_profile: List[LandlordProfile] = self._manage_if_landlord()

    @classmethod
    def create(cls, target_model: User, deleted_by: User, reason: str) -> UserCascadeDelete:
        """
        Factory method to create a UserCascadeDelete handler.

        Decides the appropriate email handler (`SoftAdminResponse` or `SoftUserResponse`)
        based on the executor and deletion reason.

        Args:
            target_model (User): User instance to delete.
            deleted_by (User): User performing the deletion.
            reason (str): Reason for deletion.

        Returns:
            UserCascadeDelete: Instance of this deletion handler.

        Raises:
            ValidationError: If the user account is already marked as deleted.
            PermissionDenied: If the executor does not have permission to perform deletion.
        """
        if target_model.is_deleted:
            raise ValidationError({'detail': _('Account data is already deleted.')})
        email_handler: Type[SoftAdminResponse | SoftUserResponse] = cls._prevalidate(target_model, deleted_by, reason)

        return cls(target_model=target_model, deleted_by=deleted_by, reason=reason, email_handler=email_handler)

    def _handle_reviews(self, parent_log: DeletionLog) -> None:
        """
        Log all reviews authored by the user prior to deletion.

        Only reviews with status 'PUBLISHED' are considered for logging.

        Args:
            parent_log (DeletionLog): Parent deletion log entry to attach review logs to.
        """
        reviews_list: List[Review] = list(
            Review.objects.filter(author_id=self.target_model.pk, status=ReviewStatus.PUBLISHED.value[0])
        )

        if reviews_list:
            self.log_model.list_handler(reviews_list, parent_log)

    @atomic_handel
    def _delete(self) -> None:
        """
        Perform the cascade soft deletion of the user and related models.

        Steps:
            1. Create a deletion log entry for the user.
            2. Log and handle reviews authored by the user.
            3. Handle company membership records if the user is a company member landlord.
            4. Log landlord profile(s) and associated properties if applicable.
            5. Soft-delete the user account itself.

        Notes:
            - Runs inside an atomic transaction to ensure all-or-nothing deletion.
            - Any exception raised here will propagate to `execute()` for handling and notifications.
        """
        parent_log: DeletionLog = self.log_model.user_log(self.target_model, self.reason)

        self._handle_reviews(parent_log)

        if self.landlord_type == self._COMPANY_MEMBER:
            self._handle_company_membership(parent_log)

        elif self.is_landlord and self.landlord_profile:
            if len(self.landlord_profile) > 1:
                self.log_model.landlord_profile_list(self.landlord_profile, parent_log)
            else:
                self.log_model.landlord_profile(self.landlord_profile, parent_log)

        self.target_model.soft_delete()

    def execute(self) -> None:
        """
        Execute the full deletion workflow for the user.

        Steps:
            1. Check for active bookings and prevent deletion if any exist.
            2. Notify via email handler if deletion cannot proceed.
            3. Perform cascade deletion via `_delete`.
            4. Send success notifications on successful deletion.
            5. Catch and log unexpected errors, invoking the email handler for error reporting.

        Exceptions:
            Any exception raised during `_delete` or notifications is handled
            by `self.email_handler.handle_error`.
        """
        try:
            has_active_bookings: List[Booking] = self._check_active_bookings()

            if has_active_bookings:
                landlord: bool = True if self.is_landlord and self.landlord_profile else False
                self.email_handler.handle_failed(has_active_bookings, landlord)
                return

            self._delete()

            self.email_handler.handle_success()
        except Exception as e:
            logger.exception(f'Failed to soft delete user {self.target_model.pk}: {e}')
            self.email_handler.handle_error()

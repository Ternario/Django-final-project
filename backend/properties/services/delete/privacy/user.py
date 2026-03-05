from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from properties.models import User, LandlordProfile, DeletionLog, UserProfile

import logging

from django.core.exceptions import ValidationError, PermissionDenied

from properties.models import Booking, Review, Discount

from properties.utils.choices.deletion import DeletionType
from properties.utils.error_messages.permission import PERMISSION_ERRORS
from properties.utils.error_messages.removed_reason import REMOVED_REASON
from properties.utils.decorators import atomic_handel
from properties.services.delete.email.privacy import PrivacyAdminResponse
from properties.services.delete.log_model.privacy import PrivacyLogModel
from properties.services.delete.class_mixin.cascade_actions_mixin import CascadeActionsMixin

from properties.tasks.service import rating_updater_task
from properties.utils.choices.landlord_profile import LandlordType
from properties.utils.choices.review import ReviewStatus

logger = logging.getLogger(__name__)


class UserCascadeDepersonalization(CascadeActionsMixin):
    """
    Handles privacy-based depersonalization of a User instance.

    Supports:
        - Anonymization (privacy delete) of the user account and profile.
        - Logging and depersonalization of related models created by the user:
            - Reviews authored by the user.
            - Bookings created by the user.
            - Discounts created by the user.
            - Bookings cancelled by the user.
        - Cascade handling of landlord-related data:
            - Company membership records if the user is a company member.
            - Landlord profiles (individual or company).
            - Booking snapshot data referencing the landlord profile.
        - Active booking checks before depersonalization.
        - Logging depersonalization events via `PrivacyLogModel`.
        - Notifications for success, failure, or unexpected errors.

    Attributes:
        PRIVACY_DELETE (str): Marker for privacy deletion type.
        target_model (User): User being depersonalized.
        deleted_by (User): Admin performing the depersonalization.
        reason (str): Reason provided for depersonalization.
        is_landlord (bool): True if the user has a landlord role.
        landlord_type (str): Type of landlord relationship (individual, company, company member).
        landlord_profile (List[LandlordProfile]): Landlord profile(s), if applicable.
        log_model (PrivacyLogModel): Logger for depersonalization.
        email_handler (PrivacyAdminResponse): Handles notifications for this process.
    """
    PRIVACY_DELETE: str = DeletionType.PRIVACY_DELETE.value[0]
    _INDIVIDUAL: str = LandlordType.INDIVIDUAL.value[0]
    _COMPANY: str = LandlordType.COMPANY.value[0]
    _COMPANY_MEMBER: str = LandlordType.COMPANY_MEMBER.value[0]

    def __init__(self, target_model: User, deleted_by: User, reason: str):
        self.target_model = target_model
        self.deleted_by = deleted_by
        self.reason = reason
        self.is_landlord: bool = target_model.is_landlord
        self.landlord_type: str = target_model.landlord_type
        self.landlord_profile: List[LandlordProfile] = self._manage_if_landlord()
        self.log_model: PrivacyLogModel = PrivacyLogModel(deleted_by, self.PRIVACY_DELETE)
        self.email_handler: PrivacyAdminResponse = PrivacyAdminResponse(target_model, deleted_by.email)

    @staticmethod
    def _prevalidate(deleted_by: User, reason: str) -> None:
        """
        Validate admin permissions and ensure a reason is provided.

        Args:
            deleted_by (User): User attempting the depersonalization.
            reason (str): Reason provided.

        Raises:
            PermissionDenied: If user is not admin.
            ValidationError: If reason is missing.
        """
        if deleted_by is None or not deleted_by.is_admin:
            raise PermissionDenied({'permission': PERMISSION_ERRORS})

        if not reason:
            raise ValidationError({'removed_reason': REMOVED_REASON})

    @classmethod
    def create(cls, target_model: User, deleted_by: User, reason: str) -> UserCascadeDepersonalization:
        """
        Factory method to create a depersonalization handler.

        Args:
            target_model (User): User to depersonalize.
            deleted_by (User): Admin performing the depersonalization.
            reason (str): Reason for depersonalization.

        Returns:
            UserCascadeDepersonalization: Instance of this handler.

        Raises:
            PermissionDenied: If `deleted_by` is not an admin.
            ValidationError: If reason is missing.
        """
        cls._prevalidate(deleted_by, reason)
        return cls(target_model=target_model, deleted_by=deleted_by, reason=reason)

    def _handle_user_profile(self) -> None:
        """
        Depersonalize the user's profile.

        Executes `privacy_delete()` on the linked `UserProfile`,
        anonymizing personal fields.

        Raises:
            ValidationError: If the user does not have an associated profile.
        """
        profile: UserProfile = self.target_model.profile
        profile.privacy_delete()

    def _handle_reviews(self, parent_log: DeletionLog) -> List[int]:
        """
        Log all reviews authored by the user before depersonalization.

        Collects property IDs for reviews affecting published or soft-deleted ratings.

        Args:
            parent_log (DeletionLog): Parent deletion log entry to attach review logs to.

        Returns:
            List[int]: Property IDs whose ratings may need recalculation.
        """
        reviews_list: List[Review] = list(Review.objects.filter(author_id=self.target_model.pk))

        property_ids: List[int] = [r.property_ref_id for r in reviews_list if r.status in [
            ReviewStatus.PUBLISHED.value[0], ReviewStatus.SOFT_DELETED.value[0]
        ]]

        if reviews_list:
            self.log_model.list_handler(reviews_list, parent_log)

        return property_ids

    def _handle_bookings(self, parent_log: DeletionLog) -> None:
        """
        Log all bookings created by the user before depersonalization.

        Args:
            parent_log (DeletionLog): Parent deletion log entry to attach booking logs to.
        """
        bookings_list: List[Booking] = list(Booking.objects.filter(guest_id=self.target_model.pk))

        if bookings_list:
            self.log_model.list_handler(bookings_list, parent_log)

    def _handle_cancelled_bookings(self) -> None:
        """
        Depersonalize all bookings cancelled by the user.

        Calls `cancelled_by_privacy_delete()` on each affected booking
        to anonymize cancellation-related data.
        """
        bookings_list: List[Booking] = list(Booking.objects.filter(cancelled_by_id=self.target_model.pk))

        for booking in bookings_list:
            booking.cancelled_by_privacy_delete()

    def _handle_discount(self, parent_log: DeletionLog) -> None:
        """
        Log all discounts created by the user before depersonalization.

        Args:
            parent_log (DeletionLog): Parent deletion log entry to attach discount logs to.
        """
        discount_list: List[Discount] = list(Discount.objects.filter(created_by_id=self.target_model.pk))

        if discount_list:
            self.log_model.list_handler(discount_list, parent_log)

    @atomic_handel
    def _delete(self):
        """
        Perform the depersonalization of the user and related models.

        Steps:
            1. Log depersonalization event for the user.
            2. Log reviews and bookings authored by the user.
            3. Depersonalize cancelled bookings and discounts if applicable.
            4. Log company membership models if the user is a company member.
            5. Log landlord profile(s) and related booking snapshot data if applicable.
            6. Execute `privacy_delete()` on the user model.
            7. Trigger rating recalculation for affected properties.

        Notes:
            - Runs inside an atomic transaction.
        """
        parent_log: DeletionLog = self.log_model.user_log(self.target_model, self.reason)

        self._handle_user_profile()
        self._handle_bookings(parent_log)

        property_ids: List[int] = self._handle_reviews(parent_log)

        if any([self.is_landlord, self.target_model.is_admin, self.target_model.is_moderator]):
            self._handle_cancelled_bookings()
            self._handle_discount(parent_log)

        if self.is_landlord and self.landlord_type == self._COMPANY_MEMBER:
            self._handle_company_membership(parent_log)

        elif self.is_landlord and self.landlord_profile:
            if len(self.landlord_profile) > 1:
                self.log_model.landlord_profile_list(self.landlord_profile, parent_log)
            else:
                self.log_model.landlord_profile(self.landlord_profile[0], parent_log)

        self.target_model.privacy_delete()

        if property_ids:
            rating_updater_task.delay(property_ids)

    def execute(self) -> None:
        """
        Execute the depersonalization workflow.

        Steps:
            1. Check for active bookings.
            2. Notify via email if depersonalization cannot proceed.
            3. Perform depersonalization via `_delete`.
            4. Send success notification.
            5. Log and handle unexpected errors.

        Exceptions:
            All exceptions are caught and handled via `self.email_handler.handle_error`.
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
            logger.exception(f'Failed to privacy delete user {self.target_model.pk}: {e}')
            self.email_handler.handle_error()

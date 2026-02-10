from __future__ import annotations
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from properties.models import (
        User, LandlordProfile, Booking, DeletionLog, Review, UserProfile, CompanyMembership, Discount
    )

import logging

from django.core.exceptions import ValidationError, PermissionDenied

from properties.utils.choices.deletion import DeletionType
from properties.utils.error_messages.permission import PERMISSION_ERRORS
from properties.utils.error_messages.removed_reason import REMOVED_REASON
from properties.utils.decorators import atomic_handel
from properties.services.delete.email.privacy import PrivacyAdminResponse
from properties.services.delete.log_model.privacy import PrivacyLogModel
from properties.services.delete.class_mixin.booking import BookingCheckMixin

logger = logging.getLogger(__name__)


class UserCascadeDepersonalization(BookingCheckMixin):
    """
    Handles privacy-based deletion (depersonalization) of a User instance.

    Supports:
        - Anonymization (privacy delete) of the user account.
        - Cascade depersonalization of related models:
            - Reviews authored by the user.
            - Bookings made by the user.
            - Landlord profiles (individual or company) and associated properties.
        - Active booking checks before depersonalization.
        - Logging of depersonalization events via `PrivacyLogModel`.
        - Notifications for success, failure, or errors.

    Attributes:
        PRIVACY_DELETE (str): Marker for privacy deletion type.
        target_model (User): User being depersonalized.
        deleted_by (User): Admin performing the depersonalization.
        reason (str): Reason provided for depersonalization.
        is_landlord (bool): True if the user is a landlord.
        landlord_profile (IndividualLandlord | List[Company] | None): Landlord profile(s), if applicable.
        log_model (PrivacyLogModel): Logger for privacy deletions.
        email_handler (PrivacyAdminResponse): Handles notifications for this process.
    """
    PRIVACY_DELETE: str = DeletionType.PRIVACY_DELETE.value[0]

    def __init__(self, target_model: User, deleted_by: User, reason: str):
        self.target_model = target_model
        self.deleted_by = deleted_by
        self.reason = reason
        self.is_landlord: bool = target_model.is_landlord
        self.landlord_profile: LandlordProfile | List[LandlordProfile] | None = (
            self._get_landlord_profile() if self.is_landlord else None
        )
        self.log_model: PrivacyLogModel = PrivacyLogModel(deleted_by, self.PRIVACY_DELETE)
        self.email_handler: PrivacyAdminResponse = PrivacyAdminResponse(target_model, deleted_by.email)

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
        return cls(target_model, deleted_by, reason)

    def _handle_user_profile(self) -> None:
        """
        Depersonalize the user's profile.

        This method attempts to access the `UserProfile` linked to the target user.
        - If found, it calls `privacy_delete()` on the profile, which anonymizes
          personal fields.

        Raises:
            ValidationError: If the user does not have an associated profile.
        """
        profile: UserProfile = self.target_model.profile
        profile.privacy_delete()

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

    def _handle_reviews(self, parent_log: DeletionLog) -> None:
        """
        Log all reviews authored by the user before depersonalization.

        Args:
            parent_log (DeletionLog): Parent deletion log entry to attach reviews logs to.
        """
        reviews_list: List[Review] = self.target_model.reviews.all()

        if reviews_list:
            self.log_model.list_handler(reviews_list, parent_log)

    def _handle_bookings(self, parent_log: DeletionLog) -> None:
        """
        Log all bookings created by the user before depersonalization.

        Args:
            parent_log (DeletionLog): Parent deletion log entry to attach bookings logs to.
        """
        bookings_list: List[Booking] = self.target_model.bookings.all()

        if bookings_list:
            self.log_model.list_handler(bookings_list, parent_log)

    def _handle_cancelled_bookings(self) -> None:
        """
        Depersonalization of all bookings that the user cancelled.
        """
        bookings_list: List[Booking] = Booking.objects.filter(cancelled_by=self.target_model)

        for booking in bookings_list:
            booking.cancelled_by_privacy_delete()

    def _handle_company_membership(self, parent_log: DeletionLog) -> None:
        """
        Logs all user membership models before depersonalization.

        Args:
            parent_log (DeletionLog): Parent deletion log entry to attach company membership logs to.
        """
        membership_list: List[CompanyMembership] = CompanyMembership.objects.filter(user=self.target_model)

        if membership_list:
            self.log_model.list_handler(membership_list, parent_log)

    def _handle_discount(self, parent_log: DeletionLog) -> None:
        """
        Logs all discounts created by user before depersonalization.

        Args:
            parent_log (DeletionLog): Parent deletion log entry to attach discount logs to.
        """
        discount_list: List[Discount] = Discount.objects.filter(created_by=self.target_model)

        if discount_list:
            self.log_model.list_handler(discount_list, parent_log)

    def _check_active_bookings(self) -> List[Booking]:
        """
        Aggregate all active bookings related to the user.

        Includes:
            - Bookings where the user is a guest.
            - Bookings for properties owned by the user's landlord profile(s).

        Returns:
            List[Booking]: Active bookings preventing depersonalization.
        """
        active_bookings: List[Booking] = self._get_active_bookings()

        if self.is_landlord and self.landlord_profile is not None:
            properties_bookings: List[Booking] = self._get_active_property_list_booking()

            if properties_bookings:
                active_bookings.extend(properties_bookings)

        return active_bookings

    def _handle_related_booking_snapshot_data(self) -> None:
        """
        Depersonalization of all bookings snapshot data that has related to individual landlord profile of the user.
        """
        booking_list: List[Booking] = Booking.objects.filter(prperty_ref=self.landlord_profile)

        if booking_list:
            for booking in booking_list:
                booking.property_owner_privacy_delete()

    @atomic_handel
    def _delete(self):
        """
        Perform the actual depersonalization of the user.

        Steps:
            1. Log depersonalization event for the user.
            2. Log reviews and bookings authored by the user.
            3. Depersonalization of cancelled bookings and discount if applicable.
            4. Log company membership models(s) if applicable.
            5. Log landlord profile(s) and booking snapshot data if applicable.
            6. Execute `privacy_delete()` on the user model.

        Notes:
            - Runs inside an atomic transaction.
        """
        parent_log: DeletionLog = self.log_model.user_log(self.target_model, self.reason)

        self._handle_user_profile()
        self._handle_reviews(parent_log)
        self._handle_bookings(parent_log)

        if any([self.is_landlord, self.target_model.is_admin, self.target_model.is_moderator]):
            self._handle_cancelled_bookings()
            self._handle_discount(parent_log)

        if self.is_landlord and not self.landlord_profile:
            self._handle_company_membership(parent_log)

        elif self.is_landlord and self.landlord_profile is not None:
            if isinstance(self.landlord_profile, list):
                self.log_model.landlord_profile_list(self.landlord_profile, parent_log)
            else:
                self._handle_related_booking_snapshot_data()
                self.log_model.landlord_profile(self.landlord_profile, parent_log)

        self.target_model.privacy_delete()

    def execute(self) -> None:
        """
        Execute the depersonalization workflow.

        Steps:
            1. Check for active bookings.
            2. Notify if depersonalization cannot proceed.
            3. Perform depersonalization via `_delete`.
            4. Send success notification.
            5. Handle and log unexpected errors.

        Exceptions are handled via `self.email_handler.handle_error`.
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

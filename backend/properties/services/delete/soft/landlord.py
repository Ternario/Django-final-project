from __future__ import annotations
from typing import TYPE_CHECKING, List, Type

if TYPE_CHECKING:
    from properties.models import LandlordProfile

import logging

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from properties.models import User, Booking
from properties.services.delete.soft.base import BaseCascadeDelete
from properties.services.delete.email.soft_admin import SoftAdminResponse
from properties.services.delete.email.soft_user import SoftUserResponse
from properties.services.delete.class_mixin.cascade_actions_mixin import CascadeActionsMixin

from properties.utils.decorators import atomic_handel

logger = logging.getLogger(__name__)


class LandlordProfileCascadeDelete(BaseCascadeDelete, CascadeActionsMixin):
    """
    Concrete implementation of `BaseCascadeDelete` for handling soft deletions
    of landlord profiles, including both individual landlords and companies.

    Supports:
        - Soft deletion of a landlord profile.
        - Cascade handling of related models, including:
            - Properties owned by the landlord.
            - Company memberships if the profile represents a company.
        - Checks for active bookings before deletion and prevents deletion if any exist.
        - Logging deletion events using `CreateLogModel`.
        - Notifications on deletion success, failure, or unexpected errors.

    Attributes:
        target_model (LandlordProfile): The landlord profile instance being deleted.
        deleted_by (User): User performing the deletion.
        reason (str | None): Reason provided for the deletion.
        log_model (SoftLogModel): Logger instance for deletions.
        email_handler (SoftAdminResponse | SoftUserResponse): Handler for sending
            email notifications depending on the deletion context.
    """

    @classmethod
    def create(cls, target_model: LandlordProfile, deleted_by: User, reason: str) -> LandlordProfileCascadeDelete:
        """
        Factory method to create a LandlordProfileCascadeDelete handler.

        Determines the appropriate email handler (`SoftAdminResponse` or `SoftUserResponse`)
        based on who performs the deletion (admin/moderator vs. creator).

        Args:
            target_model (LandlordProfile): The landlord profile to delete.
            deleted_by (User): User performing the deletion.
            reason (str): Reason for deletion.

        Returns:
            LandlordProfileCascadeDelete: Instance of this deletion handler.

        Raises:
            ValidationError: If the landlord profile is already marked as deleted.
            PermissionDenied: If the user lacks permissions to delete the profile.
        """
        if target_model.is_deleted:
            raise ValidationError({'detail': _('Landlord profile is already deleted.')})

        email_handler: Type[SoftAdminResponse | SoftUserResponse] = cls._prevalidate(
            target_model.created_by, deleted_by, reason
        )
        return cls(target_model=target_model, deleted_by=deleted_by, reason=reason, email_handler=email_handler)

    def _check_active_bookings(self) -> List[Booking]:
        """
        Retrieve all active bookings associated with properties of the given landlord profile.

        Returns:
            List[Booking]: List of active Booking instances associated with the landlord's properties.
        """
        return self._get_active_property_booking(self.target_model)

    @atomic_handel
    def _delete(self) -> None:
        """
        Perform the cascade deletion of the landlord profile and its related models.

        Steps:
            1. Log the deletion event for the landlord profile.
            2. Cascade deletion for all associated properties.
            3. Cascade deletion for company memberships if the profile is a company.

        Notes:
            - All operations run within an atomic transaction.
            - Actual cascade logic is handled via `log_model.landlord_profile`,
              ensuring consistent deletion of related objects.
        """
        self.log_model.landlord_profile(self.target_model, self.reason)

    def execute(self) -> None:
        """
        Execute the deletion workflow for the landlord profile.

        Steps:
            1. Check for active bookings associated with the profile's properties.
            2. Notify if deletion cannot proceed due to active bookings.
            3. Perform cascade deletion via `_delete`.
            4. Send success notifications upon completion.
            5. Catch and log any unexpected errors.

        Exceptions:
            Any exceptions raised during `_delete` or notifications are
            handled via `self.email_handler.handle_error`.
        """
        try:
            has_active_bookings: List[Booking] = self._check_active_bookings()

            if has_active_bookings:
                self.email_handler.handle_failed(has_active_bookings)
                return

            self._delete()

            self.email_handler.handle_success()
        except Exception as e:
            logger.exception(f'Failed to soft delete Landlord profile, id: {self.target_model.pk}: {e}')
            self.email_handler.handle_error()

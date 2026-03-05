from __future__ import annotations
from typing import TYPE_CHECKING, List, Type

if TYPE_CHECKING:
    from properties.models import Property, LandlordProfile, CompanyMembership

import logging

from django.core.exceptions import ValidationError, PermissionDenied
from django.utils.translation import gettext_lazy as _

from properties.models import User, Booking
from properties.services.delete.soft.base import BaseCascadeDelete
from properties.services.delete.email.soft_admin import SoftAdminResponse
from properties.services.delete.email.soft_user import SoftUserResponse
from properties.utils.choices.landlord_profile import CompanyRole, LandlordType
from properties.utils.error_messages.removed_reason import REMOVED_REASON
from properties.utils.error_messages.permission import PERMISSION_ERRORS
from properties.utils.decorators import atomic_handel

logger = logging.getLogger(__name__)


class PropertyDelete(BaseCascadeDelete):
    """
    Concrete implementation of `BaseCascadeDelete` for handling soft deletion
    of a single Property instance.

    Supports:
        - Soft deletion of the property.
        - Checks for active bookings before deletion.
        - Logging deletion events using `CreateLogModel`.
        - Permission validation for individual landlords and company landlords.
        - Notifications for success, failure, or unexpected errors.

    Attributes:
        target_model (Property): The property instance being deleted.
        deleted_by (User): User performing the deletion.
        reason (str | None): Reason provided for deletion.
        log_model (SoftLogModel): Logger instance for deletion events.
        email_handler (SoftAdminResponse | SoftUserResponse): Handler for sending
            email notifications depending on deletion context.
    """

    @staticmethod
    def _get_company_admins_list(company: LandlordProfile) -> List[int]:
        """
        Retrieve the list of user IDs authorized as admins for a company landlord.

        Includes the company owner and all users with `ADMIN` role.

        Args:
            company (LandlordProfile): Company landlord instance.

        Returns:
            List[int]: User IDs authorized to manage the company property.
        """
        admins: List[int] = [company.created_by.pk]

        admins.extend(
            list(CompanyMembership.objects.filter(
                company_id=company.pk, role=CompanyRole.ADMIN.value[0]
            ).values_list('user_id', flat=True))
        )

        return admins

    @classmethod
    def create(cls, target_model: Property, deleted_by: User, reason: str) -> PropertyDelete:
        """
        Factory method to create a PropertyDelete handler.

        Determines the appropriate email handler and validates permissions
        depending on whether the property belongs to an individual landlord
        or a company landlord.

        Args:
            target_model (Property): Property instance to delete.
            deleted_by (User): User performing the deletion.
            reason (str): Reason for deletion.

        Returns:
            PropertyDelete: Instance of this deletion handler.

        Raises:
            ValidationError: If the property is already deleted or reason is missing.
            PermissionDenied: If the user lacks permission to delete the property.
        """
        if target_model.is_deleted:
            raise ValidationError({'detail': _('Property is already deleted.')})

        if target_model.owner.type == LandlordType.INDIVIDUAL.value[0]:
            email_handler: Type[SoftAdminResponse | SoftUserResponse] = cls._prevalidate(
                target_model.owner.created_by, deleted_by, reason)
        else:
            admins: List[int] = cls._get_company_admins_list(target_model.owner)

            if deleted_by.pk not in admins:
                if not deleted_by.is_admin and not deleted_by.is_moderator:
                    raise PermissionDenied({'permission': PERMISSION_ERRORS})

                email_handler: Type[SoftAdminResponse] = SoftAdminResponse
            else:
                email_handler: Type[SoftUserResponse] = SoftUserResponse

            if not reason:
                raise ValidationError({'removed_reason': REMOVED_REASON})

        return cls(target_model=target_model, deleted_by=deleted_by, reason=reason, email_handler=email_handler)

    def _check_active_bookings(self) -> List[Booking]:
        """
        Retrieve all active bookings associated with this property.

        Returns:
            List[Booking]: Active Booking instances referencing the property.
        """
        return list(Booking.objects.active(property_ref=self.target_model))

    @atomic_handel
    def _delete(self) -> None:
        """
        Perform the soft deletion of the property.

        Steps:
            1. Create a deletion log for the property.
            2. Soft-delete the property instance.

        Notes:
            - All operations are executed within an atomic transaction.
            - Logging and soft deletion are handled via `log_model.single_model`,
              which ensures consistent deletion and logging of the property.
        """
        self.log_model.single_model(self.target_model, self.reason)

    def execute(self) -> None:
        """
        Execute the deletion workflow for the property.

        Steps:
            1. Check for active bookings related to the property.
            2. Notify if deletion cannot proceed due to active bookings.
            3. Perform deletion via `_delete`.
            4. Send success notifications upon completion.
            5. Catch and log any unexpected errors.

        Exceptions:
            Any exceptions raised during deletion or notifications are
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
            logger.exception(f'Failed to soft delete Property {self.target_model.pk}: {e}')
            self.email_handler.handle_error()

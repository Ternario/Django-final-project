from __future__ import annotations

from typing import TYPE_CHECKING, List, Union, Type

from properties.utils.choices.landlord_profile import LandlordType

if TYPE_CHECKING:
    from properties.models import User, LandlordProfile

from abc import ABC, abstractmethod
from django.core.exceptions import ValidationError, PermissionDenied

from properties.models import Property, Booking

from properties.services.delete.email.soft_admin import SoftAdminResponse
from properties.services.delete.email.soft_user import SoftUserResponse
from properties.services.delete.log_model.soft import SoftLogModel
from properties.utils.error_messages.removed_reason import REMOVED_REASON
from properties.utils.error_messages.permission import PERMISSION_ERRORS
from properties.utils.choices.deletion import DeletionType

DeletableModel = Union[User, LandlordProfile, Property]


class BaseCascadeDelete(ABC):
    """
    Abstract base class defining the interface and shared utilities for performing
    soft or cascade deletions on models such as User, Property, Review, Company, etc.

    This class provides:
        - Validation of permissions and deletion reason.
        - Abstract method `_check_active_bookings` to retrieve active bookings
          associated with the target model.
        - Notification handling for deletion success, failures due to active bookings,
          and unexpected errors.
        - Abstract methods `_delete` and `execute` to be implemented by subclasses
          for the actual deletion logic.

    Attributes:
        SOFT_DELETE (str): Default string representing a soft deletion type.
        target_model (DeletableModel): Model instance that is being deleted.
        deleted_by (User): User performing the deletion.
        reason (str): Reason provided for deletion.
        log_model (SoftLogModel): Logger instance for soft deletions.
        email_handler (SoftAdminResponse | SoftUserResponse): Handler for sending
            email notifications depending on the deletion context.
    """
    SOFT_DELETE: str = DeletionType.SOFT_DELETE.value[0]
    _INDIVIDUAL: str = LandlordType.INDIVIDUAL.value[0]
    _COMPANY: str = LandlordType.COMPANY.value[0]
    _COMPANY_MEMBER: str = LandlordType.COMPANY_MEMBER.value[0]

    def __init__(self, target_model: DeletableModel, deleted_by: User, reason: str,
                 email_handler: Type[SoftAdminResponse | SoftUserResponse]) -> None:
        self.target_model = target_model
        self.deleted_by = deleted_by
        self.reason = reason
        self.log_model = SoftLogModel(deleted_by, self.SOFT_DELETE)
        self.email_handler = email_handler(target_model, deleted_by.email)

    @classmethod
    @abstractmethod
    def create(cls, target_model: DeletableModel, deleted_by: User, reason: str) -> BaseCascadeDelete:
        """
        Factory method to create a deletion handler instance.

        Args:
            target_model (DeletableModel): Model instance to delete.
            deleted_by (User): User performing the deletion.
            reason (str): Reason for deletion.

        Returns:
            BaseCascadeDelete: Instance of a concrete deletion handler.

        Raises:
            ValidationError: If the target model is already deleted or reason is missing.
            PermissionDenied: If the user lacks permissions to perform deletion.
        """
        pass

    @staticmethod
    def _prevalidate(target_user: User, deleted_by: User, reason: str) -> Type[SoftAdminResponse | SoftUserResponse]:
        """
        Validate permissions and deletion reason before performing deletion.

        Args:
            target_user (User): User who is the target of deletion.
            deleted_by (User): User attempting the deletion.
            reason (str): Reason for deletion.

        Returns:
            Type[SoftAdminResponse | SoftUserResponse]: The appropriate email handler
            class depending on whether the action is self-deletion or performed by
            an administrator.

        Raises:
            PermissionDenied: If `deleted_by` is None or lacks permissions.
            ValidationError: If reason is required but missing.
        """
        if deleted_by is None:
            raise PermissionDenied({'permission': PERMISSION_ERRORS})

        if deleted_by != target_user:
            if not deleted_by.is_admin and not deleted_by.is_moderator:
                raise PermissionDenied({'permission': PERMISSION_ERRORS})

            if not reason:
                raise ValidationError({'removed_reason': REMOVED_REASON})

            return SoftAdminResponse
        return SoftUserResponse

    @abstractmethod
    def _check_active_bookings(self) -> List[Booking]:
        """
        Retrieve all active bookings related to the target model that would prevent deletion.

        Returns:
            List[Booking]: Active bookings preventing deletion.
        """
        pass

    @abstractmethod
    def _delete(self) -> None:
        """
        Execute the deletion logic (soft or cascade) for the target model.

        This method handle:
            - Logging
            - Cascade deletions
            - Database operations
        """
        pass

    @abstractmethod
    def execute(self) -> None:
        """
        Public entry point for performing the deletion.

        This method should:
            - Check for active bookings
            - Execute deletion if possible
            - Handle notifications
            - Catch and log any errors
        """
        pass

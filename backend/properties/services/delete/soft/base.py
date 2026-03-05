from __future__ import annotations

from typing import Union, Type

from properties.utils.choices.landlord_profile import LandlordType

from abc import ABC, abstractmethod
from django.core.exceptions import ValidationError, PermissionDenied

from properties.models import User, LandlordProfile, Property

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
        - Permission and reason validation before deletion.
        - Abstract method `_check_active_bookings` to retrieve active bookings
          associated with the target model.
        - Notification handling for deletion success, failures due to active bookings,
          and unexpected errors.
        - Abstract methods `_delete` and `execute` to be implemented by subclasses
          to perform the actual deletion logic.

    Attributes:
        SOFT_DELETE (str): Marker string representing a soft deletion type.
        _INDIVIDUAL (str): Landlord type for individual landlords.
        _COMPANY (str): Landlord type for company landlords.
        _COMPANY_MEMBER (str): Landlord type for company member landlords.
        target_model (DeletableModel): Model instance that is being deleted.
        deleted_by (User): User performing the deletion.
        reason (str | None): Reason provided for deletion.
        log_model (SoftLogModel): Logger instance for soft deletions.
        email_handler (SoftAdminResponse | SoftUserResponse): Handler for sending
            email notifications depending on the deletion context.
    """
    SOFT_DELETE: str = DeletionType.SOFT_DELETE.value[0]
    _INDIVIDUAL: str = LandlordType.INDIVIDUAL.value[0]
    _COMPANY: str = LandlordType.COMPANY.value[0]
    _COMPANY_MEMBER: str = LandlordType.COMPANY_MEMBER.value[0]

    def __init__(self, target_model: DeletableModel, deleted_by: User, reason: str | None,
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
        Factory method to create a concrete deletion handler.

        Args:
            target_model (DeletableModel): Model instance to delete.
            deleted_by (User): User performing the deletion.
            reason (str): Reason for deletion.

        Returns:
            BaseCascadeDelete: Instance of a concrete deletion handler.

        Raises:
            ValidationError: If the target model is already deleted or the reason is missing.
            PermissionDenied: If the user does not have permission to perform deletion.
        """
        pass

    @staticmethod
    def _prevalidate(target_user: User, deleted_by: User, reason: str) -> Type[SoftAdminResponse | SoftUserResponse]:
        """
        Validate permissions and ensure a deletion reason is provided.

        Determines whether the deletion is performed by the user themselves
        or by an administrator/moderator, and returns the corresponding email handler class.

        Args:
            target_user (User): User who is the target of deletion.
            deleted_by (User): User attempting the deletion.
            reason (str): Reason provided for deletion.

        Returns:
            Type[SoftAdminResponse | SoftUserResponse]: The appropriate email handler
            depending on whether deletion is self-performed or admin-performed.

        Raises:
            PermissionDenied: If `deleted_by` is None or lacks permissions.
            ValidationError: If a required reason is missing.
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
    def _delete(self) -> None:
        """
        Perform the actual deletion logic for the target model.

        This method should handle:
            - Logging the deletion event
            - Cascade deletions of related objects
            - Database operations to mark or remove the target instance
        """
        pass

    @abstractmethod
    def execute(self) -> None:
        """
        Public method to execute the deletion workflow.

        Responsibilities include:
            - Checking for active bookings and preventing deletion if any exist
            - Executing `_delete` if deletion can proceed
            - Handling success and failure notifications
            - Catching and logging any unexpected errors
        """
        pass

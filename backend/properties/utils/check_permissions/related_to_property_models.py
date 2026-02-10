from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from properties.models import User

from rest_framework.exceptions import PermissionDenied

from properties.utils.choices.landlord_profile import LandlordType, CompanyRole
from properties.utils.error_messages.permission import PERMISSION_ERRORS

if TYPE_CHECKING:
    from properties.models import Property


class CheckRelatedPropertyModelsPermission:
    """
    Utility class for validating whether a user has access to a specific
    `Property` and its associated `related models ` based on the user's landlord type
    and company membership.

    Access rules for individual landlords or company owners:

        - INDIVIDUAL or COMPANY:
          Full access to properties they own.

    Access rules for company members (COMPANY_MEMBER):

        - Regular company member:
          Can access associated properties if they have an active membership.

    If the user does not satisfy the corresponding rule, a `PermissionDenied`
    exception is raised.

    Attributes:
        user (User): The user whose access is being validated.
        hash_id (str): The unique hash identifier of the property owner.
        prop_id (int): The ID of the property being accessed.
    """
    _INDIVIDUAL: str = LandlordType.INDIVIDUAL.value[0]
    _COMPANY: str = LandlordType.COMPANY.value[0]
    _COMPANY_MEMBER: str = LandlordType.COMPANY_MEMBER.value[0]

    def __init__(self, user: User, hash_id: str, prop_id: int) -> None:
        self.user = user
        self.hash_id = hash_id
        self.prop_id = prop_id

    def _check_permission(self) -> None:
        """
        Internal method to check general access permissions for the user.

        - INDIVIDUAL or COMPANY: must own the property.
        - COMPANY_MEMBER: must have an active company membership associated
          with the property owner.

        Raises:
            PermissionDenied: If the user does not have access to the property.
        """
        if self.user.landlord_type not in [self._INDIVIDUAL, self._COMPANY, self._COMPANY_MEMBER]:
            raise PermissionDenied(PERMISSION_ERRORS)

        if self.user.landlord_type in [self._INDIVIDUAL, self._COMPANY]:
            if not Property.objects.filter(
                    id=self.prop_id, owner__created_by_pk=self.user.pk, owner__hash_id=self.hash_id
            ).exists():
                raise PermissionDenied(PERMISSION_ERRORS)

        else:
            if not Property.objects.filter(
                    id=self.prop_id, owner__hash_id=self.hash_id,
                    owner__company_memberships__user_pk=self.user.pk,
                    owner__company_memberships__role=CompanyRole.ADMIN.value[0],
                    owner__company_memberships__is_active=True
            ).exists():
                raise PermissionDenied(PERMISSION_ERRORS)

    def access(self) -> None:
        """
        Public method to validate access to the property.

        Raises:
            PermissionDenied: If the user does not have access rights.
        """
        self._check_permission()

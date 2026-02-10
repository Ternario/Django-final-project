from rest_framework.exceptions import PermissionDenied

from properties.models import User, LandlordProfile, CompanyMembership
from properties.utils.choices.landlord_profile import LandlordType, CompanyRole
from properties.utils.error_messages.permission import PERMISSION_ERRORS


class CheckPropertyPermission:
    """
    Utility class for validating whether a user has access to a specific
    `LandlordProfile` or its associated resources (e.g., properties) based
    on their landlord type and company membership.

    Access rules for individual landlords or company owners:

        - INDIVIDUAL or COMPANY:
          Full access to their own `LandlordProfile` and related objects.

    Access rules for company members (COMPANY_MEMBER):

        - Regular company member:
          Can access associated resources if they have an active membership.
        - Company admin:
          Full access to associated resources for update operations.

    If the user does not satisfy the corresponding rule, a `PermissionDenied`
    exception is raised.

    Attributes:
        user (User): The user whose access is being validated.
        hash_id (str): The unique hash identifier of the `LandlordProfile`.
    """

    def __init__(self, user: User, hash_id: str):
        self.user = user
        self.hash_id = hash_id

    _INDIVIDUAL: str = LandlordType.INDIVIDUAL.value[0]
    _COMPANY: str = LandlordType.COMPANY.value[0]
    _COMPANY_MEMBER: str = LandlordType.COMPANY_MEMBER.value[0]

    def _check_landlord_type(self) -> None:
        """
        Internal helper to validate that the user has a landlord type
        eligible for property or profile access.

        Raises:
            PermissionDenied: If the user's landlord type is not INDIVIDUAL,
            COMPANY, or COMPANY_MEMBER.
        """
        if self.user.landlord_type not in [self._INDIVIDUAL, self._COMPANY, self._COMPANY_MEMBER]:
            raise PermissionDenied(PERMISSION_ERRORS)

    def _check_landlord_access(self) -> None:
        """
        Internal helper to check that the user owns the target `LandlordProfile`.

        Raises:
            PermissionDenied: If the profile does not exist or does not belong
            to the user.
        """
        if not LandlordProfile.objects.not_deleted(created_by_id=self.user.pk, hash_id=self.hash_id).exists():
            raise PermissionDenied(PERMISSION_ERRORS)

    def _check_permissions(self) -> None:
        """
        Internal method to check general access permissions for the user.

        - INDIVIDUAL or COMPANY: must own the profile.
        - COMPANY_MEMBER: must have an active company membership.

        Raises:
            PermissionDenied: If the user does not have access.
        """
        self._check_landlord_type()

        if self.user.landlord_type in [self._INDIVIDUAL, self._COMPANY]:
            self._check_landlord_access()

        if not CompanyMembership.objects.not_deleted(
                company__hash_id=self.hash_id, user_id=self.user.pk, is_active=True
        ).exists():
            raise PermissionDenied(PERMISSION_ERRORS)
        return

    def _check_admin_permissions(self) -> None:
        """
        Internal method to check permissions specifically for update operations.

        - INDIVIDUAL or COMPANY: must own the profile.
        - COMPANY_MEMBER: must be an active company admin.

        Raises:
            PermissionDenied: If the user does not have update access.
        """
        self._check_landlord_type()

        if self.user.landlord_type in [self._INDIVIDUAL, self._COMPANY]:
            self._check_landlord_access()

        if not CompanyMembership.objects.not_deleted(
                company__hash_id=self.hash_id, user_id=self.user.pk, role=CompanyRole.ADMIN.value[0], is_active=True
        ).exists():
            raise PermissionDenied(PERMISSION_ERRORS)
        return

    def get_landlord_profile(self) -> LandlordProfile:
        """
        Public method to retrieve the `LandlordProfile` by `hash_id` after
        checking that the user has admin-level permissions.

        Access rules:
            - INDIVIDUAL or COMPANY user: must own the profile.
            - COMPANY_MEMBER user: must be an active company admin.

        Returns:
            LandlordProfile: The landlord profile corresponding to the given `hash_id`.

        Raises:
            PermissionDenied: If the user does not have sufficient permissions.
        """
        self._check_admin_permissions()

        return LandlordProfile.objects.get(hash_id=self.hash_id)

    def access_base(self) -> None:
        """
        Public method to check read or base access to a profile or associated objects.

        Raises:
            PermissionDenied: If the user does not have access.
        """
        self._check_permissions()

    def access_update(self) -> None:
        """
        Public method to check admin access to a associated objects.

        Raises:
            PermissionDenied: If the user does not have update permissions.
        """
        self._check_admin_permissions()

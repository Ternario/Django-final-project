from __future__ import annotations
from typing import TYPE_CHECKING, List, Dict

from drf_spectacular.utils import extend_schema

from properties.utils.error_messages.permission import PERMISSION_ERRORS

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from properties.models import User

from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404, RetrieveAPIView
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response

from properties.models import LandlordProfile, CompanyMembership
from properties.filters.query_params import CompanyMembershipFilter
from properties.permissions import IsLandlord
from properties.serializers import (
    LandlordProfileCreateSerializer, LandlordProfileBaseSerializer, LandlordProfileSerializer,
    LandlordProfilePublicSerializer, CompanyMembershipCreateSerializer, CompanyMembershipBaseSerializer,
    CompanyMembershipBasePublicSerializer, CompanyMembershipSerializer
)
from properties.utils.check_permissions.landlord_profile import (
    CheckLandlordProfilePermission, CheckCompanyMembershipPermissions
)
from properties.utils.choices.landlord_profile import CompanyRole, LandlordType


@extend_schema(
    request=LandlordProfileCreateSerializer,
    responses={200: None},
    description='Return landlord type choices / create landlord profile'
)
class LandlordProfileAV(APIView):
    """
    API view for retrieving choices and creating a new landlord profile.

    - GET: retrieve available options for creating a `LandlordProfile`,
      such as `landlord_type` (individual or company). This allows clients
      to know which values are valid when submitting data.
    - POST: create a new `LandlordProfile` using the `LandlordProfileCreateSerializer`.
      The requesting user must be authenticated, and the serializer uses
      the user from the request context.

    This view ensures that only authenticated users can access
    landlord profile creation and retrieve necessary choice data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs) -> Response:
        landlord_type: List[Dict[str, str]] = [{'key': key, 'label': label} for key, label in LandlordType.choices()]

        return Response({'landlord_type': landlord_type}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs) -> Response:
        user: User = self.request.user

        serializer: LandlordProfileCreateSerializer = LandlordProfileCreateSerializer(
            data=self.request.data, context={'user': user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LandlordProfileLAV(ListAPIView):
    """
    API view for listing landlord profiles owned by the authenticated user.

    Returns a list of non-deleted `LandlordProfile` objects created by
    the current user and matching their landlord type.
    """
    permission_classes = [IsLandlord]
    serializer_class = LandlordProfileBaseSerializer

    def get_queryset(self) -> QuerySet[LandlordProfile]:
        if getattr(self, 'swagger_fake_view', False):
            return LandlordProfile.objects.none()

        user: User = self.request.user

        if user.landlord_type in [LandlordType.INDIVIDUAL.value[0], LandlordType.COMPANY.value[0]]:
            return LandlordProfile.objects.not_deleted(created_by_id=user.pk, type=user.landlord_type)

        if user.landlord_type == LandlordType.COMPANY_MEMBER.value[0]:
            return LandlordProfile.objects.not_deleted(
                type=LandlordType.COMPANY.value[0], company_memberships__user_id=user.pk
            )
        raise PermissionDenied(PERMISSION_ERRORS)


class LandlordProfilePublicRAV(RetrieveAPIView):
    """
    Public API view for retrieving a landlord profile by hash ID.

    Returns a publicly accessible representation of a landlord profile
    with related reference data such as languages, currencies,
    and payment methods.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    queryset = LandlordProfile.objects.not_deleted()
    serializer_class = LandlordProfilePublicSerializer

    def get_object(self) -> LandlordProfile:
        hash_id: str = self.kwargs['hash_id']
        queryset: QuerySet[LandlordProfile] = self.get_queryset()

        queryset: QuerySet[LandlordProfile] = queryset.select_related('default_currency').frefearch_related(
            'languages_spoken', 'accepted_currencies', 'available_payment_methods'
        )

        return get_object_or_404(queryset, hash_id=hash_id)


class LandlordProfileRUDAV(RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting a landlord profile.

    Read access is granted to users with valid access to the profile.
    Update and delete operations are restricted to the profile owner
    (individual landlord or company owner).

    Soft deletion is applied instead of physical deletion.
    """
    permission_classes = [IsLandlord]
    queryset = LandlordProfile.objects.not_deleted()
    serializer_class = LandlordProfileSerializer

    def get_object(self) -> LandlordProfile:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']

        queryset: QuerySet[LandlordProfile] = self.get_queryset()

        if self.request.method in SAFE_METHODS:
            CheckLandlordProfilePermission(user, hash_id).execute_check()

            queryset = queryset.select_related('default_currency').prefetch_related(
                'languages_spoken', 'accepted_currencies', 'available_payment_methods'
            )

            return get_object_or_404(queryset, hash_id=hash_id)

        CheckLandlordProfilePermission(user, hash_id).execute_update()
        return get_object_or_404(queryset, created_by_id=user.pk, hash_id=hash_id)

    def destroy(self, request, *args, **kwargs) -> Response:
        instance: LandlordProfile = self.get_object()
        instance.soft_delete()

        return Response({'detail': 'Landlord Profile was deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class CompanyMembershipCAV(CreateAPIView):
    """
    API view for creating a new company membership.

    Allows company owners or company admins to add new members
    to a company profile.
    """
    permission_classes = [IsLandlord]
    queryset = CompanyMembership.objects.all()
    serializer_class = CompanyMembershipCreateSerializer

    def create(self, request, *args, **kwargs) -> Response:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']

        landlord_profile: LandlordProfile = CheckCompanyMembershipPermissions(user, hash_id).access_create()

        added_user: User = get_object_or_404(User, email=self.request.data['email'])

        serializer: CompanyMembershipCreateSerializer = self.get_serializer(
            data=self.request.data, context={'user': added_user, 'landlord_profile': landlord_profile}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CompanyMembershipLAV(ListAPIView):
    """
    API view for listing company memberships.

    - Company owners and admins can view all memberships.
    - Regular employees can only view active admin memberships.

    Supports filtering and ordering.
    """
    permission_classes = [IsLandlord]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CompanyMembershipFilter
    ordering_fields = ['joined_at', 'left_at']
    ordering = ['-joined_at']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.has_full_access = False

    def get_queryset(self) -> QuerySet[CompanyMembership]:
        if getattr(self, 'swagger_fake_view', False):
            return CompanyMembership.objects.none()

        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']

        self.has_full_access = CheckCompanyMembershipPermissions(user, hash_id).access_by_role()

        queryset: QuerySet[CompanyMembership] = CompanyMembership.objects.prefetch_related(
            'languages_spoken'
        ).not_deleted()

        if self.has_full_access:
            return queryset
        return queryset.filter(role=CompanyRole.ADMIN.value[0], is_active=True)

    def get_serializer_class(self):
        if getattr(self, 'has_full_access', False):
            return CompanyMembershipBaseSerializer
        return CompanyMembershipBasePublicSerializer


class CompanyMembershipRUDAV(RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting a company membership.

    - Company owners and admins can access and modify all memberships.
    - Regular employees can only retrieve their own membership.
    - Soft deletion is applied instead of physical deletion.
    """
    permission_classes = [IsLandlord]
    queryset = CompanyMembership.objects.not_deleted()
    serializer_class = CompanyMembershipSerializer

    def get_object(self) -> CompanyMembership:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']
        member_id: int = self.kwargs['id']

        queryset: QuerySet[CompanyMembership] = self.get_queryset()

        if self.request.method in SAFE_METHODS:
            CheckCompanyMembershipPermissions(user, hash_id).access_instance(member_id)
            queryset = queryset.prefetch_related('languages_spoken')

            return get_object_or_404(queryset, id=member_id, company__hash_id=hash_id)

        CheckCompanyMembershipPermissions(user, hash_id).access_update_instance()

        return get_object_or_404(queryset, id=member_id, company__hash_id=hash_id)

    def destroy(self, request, *args, **kwargs) -> Response:
        instance: CompanyMembership = self.get_object()
        instance.soft_delete()

        return Response({'detail': 'Company Member Profile was deleted successfully.'},
                        status=status.HTTP_204_NO_CONTENT)

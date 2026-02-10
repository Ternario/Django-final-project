from __future__ import annotations

from typing import TYPE_CHECKING

from properties.utils.choices.discount import DiscountType, DiscountStatus

if TYPE_CHECKING:
    from properties.models import User
    from django.db.models import QuerySet, Q

from base_config.settings import BASE_CURRENCY
from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView, get_object_or_404, RetrieveUpdateAPIView
)
from properties.permissions import IsLandlord, IsOwnerDiscountUser
from properties.serializers import (
    DiscountCreateSerializer, DiscountBaseSerializer, DiscountSerializer, DiscountPublicSerializer,
    DiscountPropertyCreateSerializer, DiscountPropertyBaseSerializer, DiscountPropertySerializer,
    DiscountUserCreateSerializer, DiscountUserBaseSerializer, DiscountUserSerializer,
    DiscountUserPropertyOwnerSerializer,
)

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import AllowAny, SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from properties.models import (
    Discount, LandlordProfile, Currency, DiscountProperty, DiscountUser
)
from properties.utils.check_permissions.discount import (
    CheckDiscountPermission, CheckDiscountPropertyPermission, CheckDiscountUserPermission
)


class DiscountCAV(CreateAPIView):
    """
    API view for creating a new Discount for a landlord.

    - POST: create a discount using `DiscountCreateSerializer`.

    Only accessible to users with landlord permissions (`IsLandlord`).
    Validates landlord access via `CheckDiscountPermission`.
    """
    permission_classes = [IsLandlord]
    queryset = Discount.objects.all()
    serializer_class = DiscountCreateSerializer

    def create(self, request, *args, **kwargs) -> Response:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']

        landlord_profile: LandlordProfile = CheckDiscountPermission(user, hash_id).get_landlord_profile()

        serializer: DiscountCreateSerializer = self.get_serializer(data=request.data, context={
            'user': user,
            'landlord_profile': landlord_profile
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DiscountPublicLAV(ListAPIView):
    """
    API view for listing publicly available discounts created by admins.

    - GET: retrieve a list of seasonal or referral discounts using `DiscountBaseSerializer`.

    Only includes discounts that are:
        - active (`status=ACTIVE`),
        - admin-created (`is_admin_created=True`),
        - of type seasonal or referral.

    Accessible to any user (no authentication required, `AllowAny`).
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = DiscountBaseSerializer

    def get_queryset(self) -> QuerySet[Discount]:
        return Discount.objects.filter(
            type__in=[DiscountType.SEASONAL.value[0], DiscountType.REFERRAL.value[0]],
            status=DiscountStatus.ACTIVE.value[0], is_admin_created=True
        )


class DiscountLAV(ListAPIView):
    """
    API view for listing discounts for a landlord.

    - GET: retrieve a list of discounts using `DiscountBaseSerializer`.

    Supports filtering by `status`, `type`, and `is_admin_created`.
    Supports ordering by `valid_from` and `valid_until`.

    Only accessible to users with landlord permissions (`IsLandlord`).
    Includes landlord-specific and admin-created discounts.
    """
    permission_classes = [IsLandlord]
    serializer_class = DiscountBaseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'type', 'is_admin_created']
    ordering_fields = ['valid_from', 'valid_until']
    ordering = ['-valid_from']

    def get_queryset(self) -> QuerySet[Discount]:
        if getattr(self, 'swagger_fake_view', False):
            return Discount.objects.none()

        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']

        CheckDiscountPermission(user, hash_id).base_access()

        landlord_profile: Q = Q(landlord_profile__hash_id=hash_id)
        admins_dc: Q = Q(
            discount_type=DiscountType.SEASONAL.value[0], is_admin_created=True,
            discount_properties__landlord_profile__hash_id=hash_id
        )

        return Discount.objects.filter(landlord_profile | admins_dc).distinct().select_related('created_by')


class DiscountPublicRAV(RetrieveAPIView):
    """
    Public API view for retrieving a single discount.

    - GET: retrieve discount details using `DiscountPublicSerializer`.
      Returns prices in the user's currency if logged in, or in `BASE_CURRENCY` otherwise.

    Accessible to any user (`AllowAny`).
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    queryset = Discount.objects.all()
    serializer_class = DiscountPublicSerializer

    def get_object(self) -> Discount:
        queryset: QuerySet[Discount] = self.get_queryset().select_related('currency')

        return get_object_or_404(queryset, id=self.kwargs['id'])

    def retrieve(self, request, *args, **kwargs) -> Response:
        if self.request.user:
            user: User = self.request.user

            currency: Currency = user.currency
        else:
            currency: Currency = Currency.objects.get(code=BASE_CURRENCY)

        instance: Discount = self.get_object()

        serializer: DiscountPublicSerializer = self.serializer_class(instance, context={'currency': currency})

        return Response(serializer.data, status=status.HTTP_200_OK)


class DiscountRUDAV(RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or disabling a single Discount.

    - GET: retrieve discount details with related currency and incompatibilities.
    - PATCH: update discount fields.
    - DELETE: disable discount instead of deleting it.

    Only accessible to landlords owning the discount (`IsLandlord`) with appropriate permissions.
    """
    permission_classes = [IsLandlord]
    queryset = Discount.objects.all()
    serializer_class = DiscountSerializer

    def get_object(self) -> Discount:
        if getattr(self, 'swagger_fake_view', False):
            return Discount.objects.none()

        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']
        discount_id: int = self.kwargs['id']

        queryset: QuerySet[Discount] = self.get_queryset()

        if self.request.method in SAFE_METHODS:
            CheckDiscountPermission(user, hash_id).base_access()

            queryset = queryset.select_related('currency').prefetch_related('incompatible_with')
            return get_object_or_404(queryset, id=discount_id, landlord_profile__hash_id=hash_id)

        CheckDiscountPermission(user, hash_id).update_access()
        return get_object_or_404(queryset, id=discount_id, landlord_profile__hash_id=hash_id)

    def destroy(self, request, *args, **kwargs) -> Response:
        instance: Discount = self.get_object()
        instance.set_disabled()

        return Response({'detail': 'Discount was disabled successfully.'}, status=status.HTTP_204_NO_CONTENT)


class DiscountPropertyCAV(CreateAPIView):
    """
    API view for creating DiscountProperty entries linking discounts to properties.

    - POST: create one or multiple DiscountProperty records using `DiscountPropertyCreateSerializer`.

    Only accessible to landlords (`IsLandlord`) who own the discount.
    Validates access using `CheckDiscountPropertyPermission`.
    """
    permission_classes = [IsLandlord]
    queryset = DiscountProperty.objects.all()
    serializer_class = DiscountPropertyCreateSerializer

    def create(self, request, *args, **kwargs) -> Response:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']
        discount_id: int = self.kwargs['d_id']

        landlord_profile, discount = CheckDiscountPropertyPermission(
            user, hash_id
        ).get_landlord_profile_and_discount(discount_id)

        is_list: bool = isinstance(self.request.data, list)

        serializer: DiscountPropertyCreateSerializer = self.get_serializer(
            data=self.request.data, context={
                'discount': discount,
                'landlord_profile': landlord_profile,
                'user': user,
            }, many=is_list
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DiscountPropertyLAV(ListAPIView):
    """
    API view for listing DiscountProperty entries for a landlord.

    - GET: retrieve DiscountProperty entries using `DiscountPropertyBaseSerializer`.

    Supports filtering by `discount`, `property`, `added_by`, and `is_active`.
    Supports ordering by `created_at`.

    Only accessible to landlords (`IsLandlord`) owning the properties.
    """
    permission_classes = [IsLandlord]
    serializer_class = DiscountPropertyBaseSerializer
    filterset_fields = ['discount', 'property', 'added_by', 'is_active']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self) -> QuerySet[DiscountProperty]:
        if getattr(self, 'swagger_fake_view', False):
            return DiscountProperty.objects.none()

        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']

        CheckDiscountPropertyPermission(user, hash_id).base_access()

        return DiscountProperty.objects.filter(landlord_profile__hash_id=hash_id).select_related(
            'discount', 'property'
        )


class DiscountPropertyRUV(RetrieveUpdateAPIView):
    """
    API view for retrieving or updating a single DiscountProperty.

    - GET: retrieve a DiscountProperty with related discount, property, and user info.
    - PATCH: partially update a DiscountProperty.

    Only accessible to landlords (`IsLandlord`) owning the property and discount.
    """
    permission_classes = [IsLandlord]
    queryset = DiscountProperty.objects.all()
    serializer_class = DiscountPropertySerializer

    def get_object(self) -> DiscountProperty:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']
        dp_id: int = self.kwargs['dp_id']

        queryset: QuerySet[DiscountProperty] = self.get_queryset()

        if self.request.method in SAFE_METHODS:
            CheckDiscountPropertyPermission(user, hash_id).base_access()

            queryset = queryset.select_related('discount', 'property', 'added_by')
            return get_object_or_404(queryset, id=dp_id, landlord_profile__hash_id=hash_id)

        CheckDiscountPropertyPermission(user, hash_id).update_access()
        return get_object_or_404(queryset, id=dp_id, landlord_profile__hash_id=hash_id)

    def update(self, request, *args, **kwargs) -> Response:
        user: User = self.request.user

        instance: DiscountProperty = self.get_object()

        serializer: DiscountPropertySerializer = self.get_serializer(instance, context={'user': user}, partial=True)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class DiscountUserCAV(CreateAPIView):
    """
    API view for creating DiscountUser entries for a user/booking.

    - POST: create a DiscountUser using `DiscountUserCreateSerializer`.

    Only accessible to landlords (`IsLandlord`) who own the discount.
    Booking validation is optional and handled via `CheckDiscountUserPermission`.
    """
    permission_classes = [IsLandlord]
    queryset = DiscountUser.objects.all()
    serializer_class = DiscountUserCreateSerializer

    def create(self, request, *args, **kwargs) -> Response:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']
        discount_id: int = self.kwargs['d_id']
        booking_number: str = self.request.data.get('booking_number', None)

        landlord_profile, discount, booking = CheckDiscountUserPermission(
            user, hash_id,
        ).get_landlord_profile_discount_booking(discount_id, booking_number)

        serializer: DiscountUserCreateSerializer = self.get_serializer(data=self.request.data, context={
            'user': user,
            'landlord_profile': landlord_profile,
            'booking': booking
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DiscountUserLAV(ListAPIView):
    """
    API view for listing a user's personal discounts.

    - GET: retrieve DiscountUser entries using `DiscountUserBaseSerializer`.

    Supports filtering by `status`, `is_used`, and `is_active`.
    Supports ordering by `expires_at`.

    Only accessible to the logged-in user (`IsAuthenticated`).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DiscountUserBaseSerializer
    filterset_fields = ['status']
    ordering_fields = ['expires_at']
    ordering = ['-expires_at']

    def get_queryset(self) -> QuerySet[DiscountUser]:
        if getattr(self, 'swagger_fake_view', False):
            return DiscountUser.objects.none()

        user: User = self.request.user
        return DiscountUser.objects.filter(user_id=user.pk).select_relate('discount')


class DiscountUserRAV(RetrieveAPIView):
    """
    API view for retrieving a single DiscountUser entry.

    - GET: retrieve DiscountUser using `DiscountUserSerializer`.

    Only accessible to the user who owns the discount (`IsOwnerDiscountUser`).
    """
    permission_classes = [IsOwnerDiscountUser]
    queryset = DiscountUser.objects.all()
    serializer_class = DiscountUserSerializer

    def get_object(self) -> DiscountUser:
        queryset: QuerySet[DiscountUser] = self.get_queryset()

        queryset = queryset.select_related('discount')
        discount_user: DiscountUser = get_object_or_404(queryset, id=self.kwargs['id'])

        self.check_object_permissions(self.request, discount_user)

        return discount_user


class DiscountUserPropertyOwnerLAV(ListAPIView):
    """
    API view for listing DiscountUser entries for a landlord's properties.

    - GET: retrieve DiscountUser entries using `DiscountUserBaseSerializer`.

    Supports filtering by `status`, `is_used`, and `is_active`.
    Supports ordering by `expires_at`.

    Only accessible to landlords (`IsLandlord`) owning the properties.
    """
    permission_classes = [IsLandlord]
    serializer_class = DiscountUserBaseSerializer
    filterset_fields = ['status']
    ordering_fields = ['expires_at']
    ordering = ['-expires_at']

    def get_queryset(self) -> QuerySet[DiscountUser]:
        if getattr(self, 'swagger_fake_view', False):
            return DiscountUser.objects.none()

        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']

        CheckDiscountUserPermission(user, hash_id).base_access()

        return DiscountUser.objects.filter(landlord_profile__hash_id=hash_id).select_related('discount')


class DiscountUserPropertyOwnerRUAV(RetrieveUpdateAPIView):
    """
    API view for retrieving or updating a DiscountUser for a landlord's property.

    - GET: retrieve DiscountUser with related discount, user, and assigned_by info.
    - PATCH: update DiscountUser fields.

    Only accessible to landlords (`IsLandlord`) with proper ownership/permissions.
    """
    permission_classes = [IsLandlord]
    queryset = DiscountUser.objects.all()
    serializer_class = DiscountUserPropertyOwnerSerializer

    def get_object(self) -> DiscountUser:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']

        queryset: QuerySet[DiscountUser] = self.get_queryset()

        if self.request.method in SAFE_METHODS:
            CheckDiscountUserPermission(user, hash_id).base_access()
            queryset = queryset.select_related('discount', 'user', 'assigned_by')

            return get_object_or_404(queryset, id=self.kwargs['du_id'], landlord_profile__hash_id=hash_id)

        CheckDiscountUserPermission(user, hash_id).update_access()
        return get_object_or_404(queryset, id=self.kwargs['du_id'], landlord_profile__hash_id=hash_id)

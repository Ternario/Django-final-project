from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from properties.models import User, Currency, LandlordProfile, PropertySlugHistory
    from django.db.models import QuerySet

from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import (
    CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, get_object_or_404, RetrieveAPIView
)
from rest_framework.permissions import AllowAny, SAFE_METHODS

from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from properties.models import Property
from properties.permissions import IsLandlord
from properties.serializers.property import (
    PropertySerializer, PropertyOwnerSerializer, PropertyBaseSerializer, PropertyCreateSerializer

)
from properties.filters.query_params import PropertyFilter
from properties.services.discount.calculator.discount import DiscountCalculator
from properties.services.discount.calculator.list_discount import ListDiscountCalculator
from properties.utils.check_permissions.property import CheckPropertyPermission
from properties.utils.currency import user_currency_or_default


class PropertyCAV(CreateAPIView):
    """
    API view for creating a new property.

    Allows landlords (individuals or companies) to create properties under
    their landlord profile. Company members with admin role can also create
    properties for their company profile.
    """
    permission_classes = [IsLandlord]
    queryset = Property.objects.all()
    serializer_class = PropertyCreateSerializer

    def create(self, request, *args, **kwargs) -> Response:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']

        landlord_profile: LandlordProfile = CheckPropertyPermission(user, hash_id).get_landlord_profile()

        serializer: PropertyCreateSerializer = self.get_serializer(
            data=self.request.data, context={'user': user, 'owner': landlord_profile}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PropertyPublicLAV(ListAPIView):
    """
    API view for listing all publicly visible properties.

    - GET: retrieve a list of active properties using `PropertyBaseSerializer`.
    - Supports filtering, searching, and ordering.
    - Prices are calculated and returned in the user-selected or default currency.

    Accessible by any user, including unauthenticated users.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = PropertyBaseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PropertyFilter
    ordering_fields = ['price', 'created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self) -> QuerySet[Property]:
        return Property.objects.active().select_related(
            'owner', 'detail', 'location'
        ).prefetch_related(
            'property_images'
        )

    def list(self, request, *args, **kwargs) -> Response:
        queryset: QuerySet[Property] = self.get_queryset()

        currency: Currency = user_currency_or_default(self.request)

        calculator: ListDiscountCalculator = ListDiscountCalculator(queryset, currency)
        calculated_queryset: QuerySet[Property] = calculator.calculate()

        serializer = self.get_serializer(calculated_queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PropertyOwnerPublicLAV(ListAPIView):
    """
    API view for listing all publicly visible properties
    belonging to a specific landlord profile.

    - GET: retrieve a list of active properties for the given `hash_id`
      using `PropertyBaseSerializer`.
    - Returns only properties owned by the specified landlord.
    - Prices are calculated and returned in the user-selected or default currency.

    Accessible by any user, including unauthenticated users.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = PropertyBaseSerializer

    def get_queryset(self) -> QuerySet[Property]:
        if getattr(self, 'swagger_fake_view', False):
            return Property.objects.none()

        hash_id: str = self.kwargs['hash_id']

        return Property.objects.active(owner__hash_id=hash_id).select_related(
            'owner', 'detail', 'location'
        ).prefetch_related(
            'property_images'
        )

    def list(self, request, *args, **kwargs) -> Response:
        queryset: QuerySet[Property] = self.get_queryset()

        currency: Currency = user_currency_or_default(self.request)

        calculator: ListDiscountCalculator = ListDiscountCalculator(queryset, currency)
        calculated_queryset: QuerySet[Property] = calculator.calculate()

        serializer = self.get_serializer(calculated_queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PropertyOwnerLAV(ListAPIView):
    """
    API view for listing properties of a specific landlord.

    - GET: retrieve a list of properties using `PropertySerializer`.
    - Only accessible to the landlord owner or company  members.
    - Supports filtering, searching, and ordering.
    - Prices are calculated in the user-selected or default currency.
    """
    permission_classes = [IsLandlord]
    serializer_class = PropertySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PropertyFilter
    ordering_fields = ['price', 'created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self) -> QuerySet[Property]:
        if getattr(self, 'swagger_fake_view', False):
            return Property.objects.none()

        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']

        CheckPropertyPermission(user, hash_id).access_base()

        return Property.objects.filter(owner__hash_id=hash_id).select_related(
            'owner', 'detail', 'location'
        ).prefetch_related(
            'property_images'
        )

    def list(self, request, *args, **kwargs) -> Response:
        queryset: QuerySet[Property] = self.get_queryset()

        currency: Currency = user_currency_or_default(self.request)

        calculator: ListDiscountCalculator = ListDiscountCalculator(queryset, currency)
        calculated_queryset: QuerySet[Property] = calculator.calculate()

        serializer = self.get_serializer(calculated_queryset, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PropertyPublicRAV(RetrieveAPIView):
    """
    API view for retrieving a single property by ID.

    - GET: retrieve detailed property information using `PropertySerializer`.
    - Includes related objects such as owner, location, amenities, images, and cancellation policy.
    - Prices are calculated in the user-selected or default currency.

    Accessible to any user.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    queryset = Property.objects.active()
    serializer_class = PropertySerializer

    def get_object(self) -> Property:
        p_lookup: int | str = self.kwargs['p_lookup']
        queryset: QuerySet[Property] = self.get_queryset().select_related(
            'owner', 'detail', 'location', 'cancellation_policy'
        ).prefetch_related(
            'amenities', 'payment_types', 'property_images'
        )

        if str(p_lookup).isdigit():
            return get_object_or_404(queryset, id=int(p_lookup))

        prop_obj: Property = queryset.filter(slug=p_lookup).first()

        if prop_obj:
            return prop_obj

        old_slug: PropertySlugHistory = PropertySlugHistory.objects.filter(old_slug=p_lookup).select_related(
            'property_ref'
        ).first()

        if old_slug:
            return old_slug.property_ref

        raise get_object_or_404(Property, pk=0)

    def retrieve(self, request, *args, **kwargs) -> Response:
        user: User = self.request.user
        currency: Currency = user_currency_or_default(self.request)

        p_lookup = self.kwargs['p_lookup']
        instance: Property = self.get_object()

        if not str(p_lookup).isdigit() and p_lookup != str(instance.slug):
            redirect_url = request.build_absolute_uri(f"/property/{instance.slug}/")

            return Response({
                'redirect': True,
                'new_slug': instance.slug,
                'url': redirect_url
            }, status=status.HTTP_301_MOVED_PERMANENTLY)

        calculator = DiscountCalculator(user, instance, currency)
        instance.pricing = calculator.calculate()

        serializer: PropertySerializer = self.get_serializer(instance)

        return Response(serializer.data, status=status.HTTP_200_OK)


class PropertyOwnerRUDV(RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting a property for its owner.

    - GET: retrieve detailed property information (accessible to owner or company member).
    - PATCH/PUT: update property fields (accessible to owner or company admin).
    - DELETE: soft delete the property (accessible to owner or company admin).
    - Prices are calculated in the default currency.

    Only accessible to the landlord owner or company admin members.
    """
    permission_classes = [IsLandlord]
    queryset = Property.objects.all()
    serializer_class = PropertyOwnerSerializer

    def get_object(self) -> Property:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']

        queryset: QuerySet[Property] = self.get_queryset()

        if self.request.method in SAFE_METHODS:
            CheckPropertyPermission(user, hash_id).access_base()

            queryset = queryset.select_related(
                'owner', 'detail', 'location', 'cancellation_policy'
            ).prefetch_related(
                'amenities', 'payment_types', 'property_images'
            )

            return get_object_or_404(queryset, id=self.kwargs['p_id'], owner__hash_id=hash_id)

        CheckPropertyPermission(user, hash_id).access_update()

        return get_object_or_404(queryset, id=self.kwargs['p_id'], owner__hash_id=hash_id)

    def retrieve(self, request, *args, **kwargs) -> Response:
        currency: Currency = user_currency_or_default(self.request)

        instance: Property = self.get_object()

        calculator = DiscountCalculator(None, instance, currency)
        instance.pricing = calculator.calculate()

        serializer: PropertySerializer = self.get_serializer(instance)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs) -> Response:
        instance: Property = self.get_object()
        instance.soft_delete()

        return Response({'detail': 'Property was deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

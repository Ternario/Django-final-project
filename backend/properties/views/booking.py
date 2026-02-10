from __future__ import annotations

from typing import TYPE_CHECKING, List, Type, Dict

from drf_spectacular.utils import extend_schema

if TYPE_CHECKING:
    from properties.models import User, Property
    from rest_framework.serializers import Serializer
    from django.db.models import QuerySet

from rest_framework.views import APIView
from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveUpdateAPIView, get_object_or_404
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from properties.permissions import IsOwnerBooking, IsLandlord
from properties.models import Booking
from properties.serializers import (
    BookingCreateSerializer, BookingBaseSerializer, BookingGuestSerializer, BookingCancellationSerializer,
    BookingOwnerSerializer
)

from properties.filters.query_params import BookingFilter
from properties.utils.check_permissions.booking import CheckBookingPermission, CheckBookingCreatePermission
from properties.utils.choices.time import CheckInTime, CheckOutTime


@extend_schema(
    request=None,
    responses={200: None},
    description='Return check in/out time choices.'
)
class BookingTimeChoicesAV(APIView):
    """
    View to get list of check in and check out time.

    Example of GET request:
    GET /properties/choices/

    Response:
    {
        'check_in_time': [{'value': '11:00:00', 'label': '11:00'}, ...],
        'check_out_time':  [{'value': '10:00:00', 'label': '10:00'}, ...]
    }

    Permissions:
            - IsAuthenticated: can only be used by an authorized user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs) -> Response:
        check_in: List[Dict[str, str]] = [{'key': key, 'label': label} for key, label in CheckInTime.choices()]
        check_out: List[Dict[str, str]] = [{'key': key, 'label': label} for key, label in CheckOutTime.choices()]

        return Response(
            {
                'check_in_time': check_in,
                'check_out_time': check_out
            },
            status=status.HTTP_200_OK
        )


class BookingCAV(CreateAPIView):
    """
    API view for creating a new Booking.

    Allows authenticated users (guests) to create a booking using the
    `BookingCreateSerializer`. Only POST requests are supported.
    """
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.all()
    serializer_class = BookingCreateSerializer

    def create(self, request, *args, **kwargs) -> Response:
        user: User = self.request.user
        prop_id: int = self.kwargs['id']

        property_ref: Property = CheckBookingCreatePermission(user, prop_id).check_and_get_property()

        serializer: BookingCreateSerializer = self.get_serializer(
            data=self.request.data, context={'user': user, 'property_ref': property_ref}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BookingLAV(ListAPIView):
    """
    API view for listing bookings of the authenticated guest.

    Returns a list of bookings where the current user is the guest.
    Supports filtering via `BookingFilter` and optimized related
    selection for `property_ref` and `currency`.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BookingBaseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookingFilter

    def get_queryset(self) -> QuerySet[Booking]:
        user: User = self.request.user
        return Booking.objects.filter(guest_id=user.pk).select_related('property_ref', 'currency')


class BookingRUAV(RetrieveUpdateAPIView):
    """
    API view for retrieving or updating a single Booking by ID.

    - GET: retrieve detailed booking information using `BookingGuestSerializer`.
    - PATCH: update or cancel the booking using `BookingCancellationSerializer`.

    Only the booking owner (guest) has permission to access this view.
    """
    queryset = Booking.objects.all()
    permission_classes = [IsOwnerBooking]

    def get_serializer_class(self) -> Type[Serializer]:
        if self.request.method in ['PATCH']:
            return BookingCancellationSerializer
        return BookingGuestSerializer

    def get_object(self) -> Booking:
        queryset: QuerySet[Booking] = self.get_queryset()

        if self.request.method in SAFE_METHODS:
            queryset = queryset.select_related('property_ref', 'currency', 'payment_type', 'payment_method')

        booking: Booking = get_object_or_404(queryset, id=self.kwargs['id'])

        self.check_object_permissions(self.request, booking)

        return booking


class BookingPropertyOwnerLAV(ListAPIView):
    """
    API view for listing bookings of a property owned by a landlord.

    Retrieves bookings for properties linked to the landlord profile specified
    by `hash_id` in the URL. Only accessible to users with landlord permissions.
    Supports filtering via `BookingFilter` and optimizes related selection
    for `property_ref` and `currency`.
    """
    permission_classes = [IsLandlord]
    serializer_class = BookingBaseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = BookingFilter

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Booking.objects.none()

        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']

        CheckBookingPermission(user, hash_id).execute()

        return Booking.objects.filter(property_ref__owner__hash_id=hash_id).select_related(
            'property_ref', 'currency'
        )


class BookingPropertyOwnerRUAV(RetrieveUpdateAPIView):
    """
    API view for retrieving or updating a single Booking for a landlord's property.

    - GET: retrieve detailed booking information using `BookingOwnerSerializer`.
    - PATCH: update or cancel the booking using `BookingCancellationSerializer`.

    Only accessible to users with landlord permissions for the property.
    """
    permission_classes = [IsLandlord]
    queryset = Booking.objects.all()

    def get_serializer_class(self) -> Type[Serializer]:
        if self.request.method in ['PATCH']:
            return BookingCancellationSerializer
        return BookingOwnerSerializer

    def get_object(self) -> Booking:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']

        CheckBookingPermission(user, hash_id).execute()

        queryset: QuerySet[Booking] = self.get_queryset()

        if self.request.method in SAFE_METHODS:
            queryset = queryset.select_related(
                'property_ref', 'guest', 'currency', 'payment_type', 'payment_method'
            )

        return get_object_or_404(queryset, property_ref__owner__hash_id=hash_id, id=self.kwargs['id'])

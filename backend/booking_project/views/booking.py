from rest_framework.generics import (
    CreateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView, get_object_or_404
)
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from booking_project.models import Booking
from booking_project.serializers.booking import (
    BookingCreateSerializer, BookingBaseDetailsSerializer, BookingDetailsPlacementOwnerSerializer,
    BookingDetailsOwnerSerializer
)
from booking_project.permissions import IsOwnerBooking, IsOwnerPlacementRelatedModels

from booking_project.serializers.choices import BookingTimeChoicesSerializer


class BookingTimeChoicesRetrieveView(RetrieveAPIView):
    """
    View to get list of check in and check out time.

    Example of GET request:
    GET /booking/choices/

    Response:
    {
        'check_in_time': [{'value': '11:00:00', 'label': '11:00'}, ...],
        'check_out_time':  [{'value': '10:00:00', 'label': '10:00'}, ...]
    }

    Permissions:
            - IsAuthenticated: can only be used by an authorized user.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = BookingTimeChoicesSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer({})

        return Response(serializer.data, status=status.HTTP_200_OK)


class BookingCreateView(CreateAPIView):
    """
    View to create new Booking.

    Example of POST request:
    POST /booking/
    {
        'placement': Placement ID (1),
        'check_in_date': '01-07-2025',
        'check_out_date': '10-07-2025',
        'check_in_time': '13:00:00', (optional, default 11:00:00)
        'check_out_time': '07:00:00', (optional, default 10:00:00)
    }

    Response:
    {
        'id': 1,
        'placement_name': 'Placement Title',
        'check_in_time': '13:00',
        'check_out_time': '07:00',
        'check_in_date': "01-07-2025",
        'check_out_date': '10-07-2025',
        'placement': 1,
        'user': 1,
    }

    Permissions:
            - IsAuthenticated: can only be used by an authorized user.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BookingCreateSerializer

    def create(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(data=request.data, context={'user': user})

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingPlacementOwnerListView(ListAPIView):
    """
    View to get list of bookings of landlord placements.

    Example of GET request:
    GET /booking/owner/

    Response:
    {
        [
            {
                'id': 1,
                'placement': 1,
                'placement_name': 'Placement Title',
                'check_in_date': '01-07-2025',
                'check_out_date': '10-07-2025',
                'status': 'Confirmed',
            },
            ...
        ]
    }

    Permissions:
            - IsOwnerPlacementRelatedModels: can only be used by an authorized landlord user.
    """
    permission_classes = [IsOwnerPlacementRelatedModels]
    serializer_class = BookingBaseDetailsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        user = self.request.user

        queryset = Booking.objects.filter(placement__owner=user)

        for obj in queryset:
            self.check_object_permissions(self.request, obj)

        return queryset


class BookingOwnerListView(ListAPIView):
    """
    View to get list of user bookings.

    Example of GET request:
    GET /booking/user/

    Response:
    {
        [
            {
                'id': 1,
                'placement': 1,
                'placement_name': 'Placement Title',
                'check_in_date': '01-07-2025',
                'check_out_date': '10-07-2025',
                'status': 'Confirmed',
            },
            ...
        ]
    }

    Permissions:
            - IsOwnerBooking: can only be used by an authorized user and get info only about his bookings.
    """
    permission_classes = [IsOwnerBooking]
    serializer_class = BookingBaseDetailsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        user = self.request.user

        queryset = Booking.objects.filter(user=user)

        for obj in queryset:
            self.check_object_permissions(self.request, obj)

        return queryset


class InactiveBookingPlacementOwnerListView(ListAPIView):
    """
    View to get list of inactive bookings to landlord's placements.

    Example of GET request:
    GET /booking/owner/inactive/

    Response:
    {
        [
            {
                'id': 1,
                'placement': 1,
                'placement_name': 'Placement Title',
                'check_in_date': '01-07-2025',
                'check_out_date': '10-07-2025',
                'status': 'Completed',
            },
            ...
        ]
    }

    Permissions:
            - IsOwnerPlacementRelatedModels: can only be used by an authorized landlord user.
    """
    permission_classes = [IsOwnerPlacementRelatedModels]
    serializer_class = BookingBaseDetailsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        user = self.request.user

        queryset = Booking.inactive_objects.filter(placement__owner=user)

        for obj in queryset:
            self.check_object_permissions(self.request, obj)

        return queryset


class InactiveBookingOwnerListView(ListAPIView):
    """
    View to get inactive list of user bookings.

    Example of GET request:
    GET /booking/user/inactive/

    Response:
    {
        [
            {
                'id': 1,
                'placement': 1,
                'placement_name': 'Placement Title',
                'check_in_date': '01-07-2025',
                'check_out_date': '10-07-2025',
                'status': 'Completed',
            },
            ...
        ]
    }

    Permissions:
            - IsOwnerBooking: can only be used by an authorized user and get info only about his bookings.
    """
    permission_classes = [IsOwnerBooking]
    serializer_class = BookingBaseDetailsSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        user = self.request.user

        queryset = Booking.inactive_objects.filter(user=user)

        for obj in queryset:
            self.check_object_permissions(self.request, obj)

        return queryset


class BookingPlacementOwnerRetrieveUpdateView(RetrieveUpdateAPIView):
    """
    View to get, update the landlord's booking by id that other user have reserved.

    Example of GET request:
    GET /booking/owner/1/

    Response:
    {
       'id': 1,
       'user': {
            'id': 1,
            'email': 'user@example.com',
            'first_name': 'User',
            'last_name': 'User',
            'username': 'UserName'
            },
       'placement_name': 'Placement Title',
       'check_in_time': '11:00',
       'check_out_time': '10:00',
       'cancelled_at': None,
       'cancelled_by_role': None,
       'check_in_date': '01-07-2025',
       'check_out_date': '10-07-2025',
       'status': 'Pending',
       'cancellation_reason': None,
       'created_at': '01-06-2025',
       'updated_at': '01-06-2025',
       'placement': 1,
       'cancelled_by': None,
    }

    Example of PUT request:
    PUT /booking/owner/1/
    {
        'cancellation_reason': 'reason' ( min 40 characters)
    }

    Response:

    {
        'id': 1,
        'user': {
            'id': 1,
            'email': 'user@example.com',
            'first_name': 'User',
            'last_name': 'User',
            'username': 'UserName'
            },
        'placement_name': 'Placement Title',
        'check_in_time': '11:00',
        'check_out_time': '10:00',
        'cancelled_at': '11-06-2025 17:37',
        'cancelled_by_role': 'Owner',
        'check_in_date': '01-07-2025',
        'check_out_date': '10-07-2025',
        'status': 'Cancelled',
        'cancellation_reason': 'reason',
        'created_at': '01-06-2025',
        'updated_at': '11-06-2025',
        'placement': 1,
        'cancelled_by': 2
    }

    Permissions:
            - IsOwnerPlacementRelatedModels: can only be used by an authorized landlord user.
    """
    permission_classes = [IsOwnerPlacementRelatedModels]
    serializer_class = BookingDetailsPlacementOwnerSerializer

    def get_object(self):
        booking = get_object_or_404(Booking.all_objects, pk=self.kwargs['pk'])

        self.check_object_permissions(self.request, booking)

        return booking


class BookingOwnerRetrieveUpdateView(RetrieveUpdateAPIView):
    """
    View to get, update the user's booking by id.

    Example of GET request:
    GET /booking/user/1/

    Response:
    {
       'id': 1,
       'placement_name': 'Placement Title',
       'check_in_time': '11:00',
       'check_out_time': '10:00',
       'cancelled_at': None,
       'cancelled_by_role': None,
       'check_in_date': '01-07-2025',
       'check_out_date': '10-07-2025',
       'status': 'Pending',
       'cancellation_reason': None,
       'created_at': '01-06-2025',
       'updated_at': '01-06-2025',
       'placement': 1,
       'cancelled_by': None,
    }

    Example of PUT request:
    PUT /booking/user/1/
    {
        'cancellation_reason': 'reason' ( min 40 characters)
    }

    Response:

    {
        'id': 1,
        'placement_name': 'Placement Title',
        'check_in_time': '11:00',
        'check_out_time': '10:00',
        'cancelled_at': '11-06-2025 17:37',
        'cancelled_by_role': 'User',
        'check_in_date': '01-07-2025',
        'check_out_date': '10-07-2025',
        'status': 'Cancelled',
        'cancellation_reason': 'reason',
        'created_at': '01-06-2025',
        'updated_at': '11-06-2025',
        'placement': 1,
        'cancelled_by': 2
    }

    Permissions:
            - IsOwnerBooking: can only be used by an authorized user and get info only about his bookings.
    """
    permission_classes = [IsOwnerBooking]
    serializer_class = BookingDetailsOwnerSerializer

    def get_object(self):
        booking = get_object_or_404(Booking.all_objects, pk=self.kwargs['pk'])

        self.check_object_permissions(self.request, booking)

        return booking

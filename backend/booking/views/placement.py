from django.db.models import Avg, Count, F, Prefetch
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import (
    CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, UpdateAPIView, get_object_or_404
)
from rest_framework.permissions import AllowAny, SAFE_METHODS
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from booking.models import Placement, Review
from booking.permissions import IsLandLord, IsOwnerPlacement
from booking.serializers.placement import (
    PlacementCreateSerializer, PlacementBaseDetailsSerializer, PlacementAllDetailsSerializer,
    PlacementSerializer, PlacementActivationSerializer
)

from booking.filters.query_params import PlacementFilter


class PlacementCreateView(CreateAPIView):
    """
    View to create new Placement.

    Example of POST request:
    POST /placement/create/
    {
        "placement_location": {
            "country": "Country name",
            "city": "City name",
            "post_code": "34567",
            "street": "Street name",
            "house_number": "House number"
        },
        "category": Category ID (7),
        "title": "Title",
        "description": "Description",
        "price": 123,
        "number_of_rooms": 2,
        "placement_area": 40,
        "total_beds": 2,
        "single_bed": 1,
        "double_bed": 1,
    }

    Response:
    {
        'id': 1,
        'title': 'Title',
        'description': 'Description',
        'price': '123.00',
        'number_of_rooms': 2,
        'placement_area': '40.00',
        'total_beds': 2,
        'single_bed': 1,
        'double_bed': 1,
        'created_at': '2025-03-19',
        'owner': 7,
        'category': 7
    }

    Permissions:
         - IsLandLord: can only be used by users who are landlords.
         - IsAuthenticated: can only be used by an authorized user.
    """

    permission_classes = [IsLandLord]
    serializer_class = PlacementCreateSerializer

    def create(self, request, *args, **kwargs):
        user = request.user

        serializer = self.get_serializer(data=request.data, context={'user': user})

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlacementsListView(ListAPIView):
    """
    View to get a list of placements.

    Example of GET request:
    GET /placement/

    Example of GET request with query parameters:
    GET /placement/?city=City name&price_gte=150&price_lte=400


    Response:
    [
        {
            'id': 1,
            'city': 'City name',
            'placement_image': [List of images],
            'rating': 4,
            'category_name': 'Hotels',
            'title': 'Placement title',
            'description': 'Description',
            'price': '550.00',
            'number_of_rooms': 2,
            'placement_area': '43.50',
            'total_beds': 3,
            'single_bed': 2,
            'double_bed': 1,
            'created_at': '2025-03-18'
        },
        .....
    ]


    Permissions:
         - AllowAny: This view is accessible without any authentication.
    """

    permission_classes = [AllowAny]
    serializer_class = PlacementBaseDetailsSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PlacementFilter
    ordering_fields = ['price', 'created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        return Placement.objects.annotate(
            city=F('placement_location__city'),
            avg_rating=Avg('reviews__rating'),
            reviews_count=Count('reviews')
        ).select_related('placement_location')


class MyPlacementsListView(ListAPIView):
    """
    View to get a list of active placements by landlord owner user.

    Example of GET request with query parameters:
    GET /placement/my/active/

    Response:
    [
        {
            'id': 1,
            'city': 'City name',
            'placement_image': [List of images],
            'rating': 4,
            'category_name': 'Hotels',
            'title': 'Placement title',
            'description': 'Description',
            'price': '550.00',
            'number_of_rooms': 2,
            'placement_area': '43.50',
            'total_beds': 3,
            'single_bed': 2,
            'double_bed': 1,
            'created_at': '2025-03-18'
        },
        .....
    ]


    Permissions:
         - IsLandLord: can only be used by users who are landlords.
         - OnlyOwnerPlacement: can only be used by the owner of the Placements.
         - IsAuthenticated: can only be used by an authorized user.
    """

    permission_classes = [IsOwnerPlacement]
    serializer_class = PlacementBaseDetailsSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PlacementFilter
    ordering_fields = ['price', 'created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        queryset = Placement.objects.filter(owner=user).annotate(
            city=F('placement_location__city'),
            avg_rating=Avg('reviews__rating'),
            reviews_count=Count('reviews')
        )

        for obj in queryset:
            self.check_object_permissions(self.request, obj)

        return queryset


class PlacementRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    View to get full details, update or destroy active placements by id.

    Example of GET request:
    GET /placement/1/

    Response:
    {
        'id': 9,
        'rating': 0,
        'placement_details': {
            'placement': 9,
            'pets': True,
            'free_wifi': False,
            'smoking': False,
            'parking': False,
            'room_service': True,
            'front_desk_allowed_24': False,
            'free_cancellation': False,
            'balcony': True,
            'air_conditioning': False,
            'washing_machine': False,
            'kitchenette': False,
            'tv': False,
            'coffee_tee_maker': True,
        },
        'placement_location': {
            'placement': 9,
            'country': 'Country nmae',
            'city': 'City name',
            'post_code': '10405',
            'street': 'Street name',
            'house_number': '1',
        },
        'placement_image': [],
        'category_name': 'Category name',
        'title': 'Placement title',
        'description': 'Description',
        'price': '250.00',
        'number_of_rooms': 2,
        'placement_area': '43.50',
        'total_beds': 3,
        'single_bed': 2,
        'double_bed': 1,
        'created_at': '2025-03-19',
        'updated_at': '2025-03-19',
        'category': 9
    }

    Example of PUT request:
    PUT /placement/1/

    {
        'category_name': 'Another Category name',
        'title': 'Another Placement title',
        'description': 'Another Description',
        'price': '250.00',
        'number_of_rooms': 2,
        'placement_area': '43.50',
        'total_beds': 3,
        'single_bed': 2,
        'double_bed': 1,
        'created_at': '2025-03-19',
        'updated_at': '2025-03-19',
        'category': 9
    }

    Response:
    {
        'category_name': 'Another Category name',
        'title': 'Another Placement title',
        'description': 'Another Description',
        'price': '250.00',
        'number_of_rooms': 2,
        'placement_area': '43.50',
        'total_beds': 3,
        'single_bed': 2,
        'double_bed': 1,
        'created_at': '2025-03-19',
        'updated_at': '2025-03-19',
        'category': 9
    }

    Example of DELETE request:
    DELETE /placement/1/

    Response: 204 No Content

    Permissions:
         - IsLandLord: can only be used by users who are landlords in Update or Destroy requests.
         - IsOwnerPlacement: can Update or Destroy only if user is owner of placement.
         - IsAuthenticatedOrReadOnly: any can retrieve info about placement,
        for Updating or Destroying the user must be authenticated.
    """

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        return [IsOwnerPlacement()]

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return PlacementSerializer
        return PlacementAllDetailsSerializer

    def get_object(self):
        queryset = Placement.objects.select_related('placement_location', 'placement_details').prefetch_related(
            'placement_images', Prefetch('reviews', queryset=Review.objects.only('rating'))).annotate(
            avg_rating=Avg('reviews__rating'))

        placement = get_object_or_404(queryset, pk=self.kwargs['pk'])

        self.check_object_permissions(self.request, placement)

        return placement


class PlacementActivationView(UpdateAPIView):
    """
    View to activate/deactivate the Placement by id.

    Example of POST request:
    POST /placement/1/activation/

    {
        'activate': True or False
    }

    Response:

    {
        'activate': 'Announcement successfully activated.'
    }

        or

    {
        'activate': 'Announcement successfully deactivated.'
    }

    Permissions:
         - IsLandLord: can only be used by users who are landlords.
         - OnlyOwnerPlacement: can only be used by the owner of the Placement.
         - IsAuthenticated: can only be used by an authorized user.
    """

    permission_classes = [IsOwnerPlacement]
    serializer_class = PlacementActivationSerializer

    def get_object(self):
        placement = get_object_or_404(Placement.all_objects, pk=self.kwargs['pk'])

        self.check_object_permissions(self.request, placement)

        return placement

    def update(self, request, *args, **kwargs):
        placement = self.get_object()

        serializer = self.get_serializer(placement, data=request.data)

        if serializer.is_valid(raise_exception=True):
            data = serializer.save()

            return Response({'activate': data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InactivePlacementListView(ListAPIView):
    """
    View to get a list of inactive placements by landlord owner user.

    Example of GET request with query parameters:
    GET /placement/my/inactive/

    Response:
    [
        {
            'id': 1,
            'city': 'City name',
            'placement_image': List of images,
            'rating': 4,
            'category_name': 'Hotels',
            'title': 'Placement title',
            'description': 'Description',
            'price': '550.00',
            'number_of_rooms': 2,
            'placement_area': '43.50',
            'total_beds': 3,
            'single_bed': 2,
            'double_bed': 1,
            'created_at': '2025-03-18'
        },
        .....
    ]

    Permissions:
         - IsLandLord: can only be used by users who are landlords.
         - OnlyOwnerPlacement: can only be used by the owner of the Placements.
         - IsAuthenticated: can only be used by an authorized user.
    """

    permission_classes = [IsOwnerPlacement]
    serializer_class = PlacementBaseDetailsSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PlacementFilter
    ordering_fields = ['price', 'created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user

        queryset = Placement.inactive_objects.filter(owner=user).annotate(
            city=F('placement_location__city'),
            avg_rating=Avg('reviews__rating'),
            reviews_count=Count('reviews')
        ).order_by('created_at')

        for obj in queryset:
            self.check_object_permissions(self.request, obj)
        return queryset


class InactivePlacementRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    """
    View to get full details of inactive placements by id only for owner user.

    Example of GET request:
    GET /placement/1/inactive/

    Response:
    {
        'id': 9,
        'rating': 0,
        'placement_details': {
            'placement': 9,
            'pets': True,
            'free_wifi': False,
            'smoking': False,
            'parking': False,
            'room_service': True,
            'front_desk_allowed_24': False,
            'free_cancellation': False,
            'balcony': True,
            'air_conditioning': False,
            'washing_machine': False,
            'kitchenette': False,
            'tv': False,
            'coffee_tee_maker': True,
        },
        'placement_location': {
            'placement': 9,
            'country': 'Country nmae',
            'city': 'City name',
            'post_code': '10405',
            'street': 'Street name',
            'house_number': '1',
        },
        'placement_image': [],
        'category_name': 'Category name',
        'title': 'Placement title',
        'description': 'Description',
        'price': '250.00',
        'number_of_rooms': 2,
        'placement_area': '43.50',
        'total_beds': 3,
        'single_bed': 2,
        'double_bed': 1,
        'created_at': '2025-03-19',
        'updated_at': '2025-03-19',
        'category': 9
    }

    Example of PUT request:
    PUT /placement/1/inactive/

    {
        'category_name': 'Another Category name',
        'title': 'Another Placement title',
        'description': 'Another Description',
        'price': '250.00',
        'number_of_rooms': 2,
        'placement_area': '43.50',
        'total_beds': 3,
        'single_bed': 2,
        'double_bed': 1,
        'created_at': '2025-03-19',
        'updated_at': '2025-03-19',
        'category': 9
    }

    Response:
    {
        'category_name': 'Another Category name',
        'title': 'Another Placement title',
        'description': 'Another Description',
        'price': '250.00',
        'number_of_rooms': 2,
        'placement_area': '43.50',
        'total_beds': 3,
        'single_bed': 2,
        'double_bed': 1,
        'created_at': '2025-03-19',
        'updated_at': '2025-03-19',
        'category': 9
    }

    Example of DELETE request:
    DELETE /placement/1/inactive/

    Response: 204 No Content

    Permissions:
         - IsLandLord: can only be used by users who are landlords.
         - OnlyOwnerPlacement: can only be used by the owner of the Placement.
         - IsAuthenticated: can only be used by an authorized user.
    """

    permission_classes = [IsOwnerPlacement]

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return PlacementSerializer
        return PlacementAllDetailsSerializer

    def get_object(self):
        queryset = Placement.inactive_objects.select_related(
            'placement_location',
            'placement_details'
        ).prefetch_related(
            'placement_images',
            Prefetch('reviews',
                     queryset=Review.objects.only('rating')
                     )
        ).annotate(
            avg_rating=Avg('reviews__rating'))

        placement = get_object_or_404(queryset, pk=self.kwargs['pk'])

        self.check_object_permissions(self.request, placement)

        return placement

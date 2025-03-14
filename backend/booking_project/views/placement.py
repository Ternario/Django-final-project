from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, UpdateAPIView, \
    get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response

from booking_project.models import Placement
from booking_project.permissions import IsLandLord, IsOwnerPlacement
from booking_project.serializers.placement import (
    PlacementCreateSerializer, PlacementBaseDetailSerializer,
    PlacementSerializer, PlacementActivationSerializer
)


class PlacementCreateView(CreateAPIView):
    permission_classes = [IsLandLord, IsAuthenticated]
    queryset = Placement.objects.all()
    serializer_class = PlacementCreateSerializer


class PlacementListView(ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PlacementBaseDetailSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        'category__name': ['exact'],
        'price': ['gte', 'lte'],
        'number_of_rooms': ['gte', 'lte']
    }
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']

    def get_queryset(self):
        location = self.request.query_params.get('city')

        if location:
            return Placement.objects.filter(placement_location__city=location, is_active=True)
        else:
            return Placement.objects.filter(is_active=True)


class PlacementRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerPlacement, IsAuthenticatedOrReadOnly]
    serializer_class = PlacementSerializer

    def get_object(self):
        placement = get_object_or_404(Placement, pk=self.kwargs['pk'])

        self.check_object_permissions(self.request, placement)

        return placement


class PlacementActivationView(UpdateAPIView):
    permission_classes = [IsOwnerPlacement, IsAuthenticated]
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
    permission_classes = [IsOwnerPlacement, IsAuthenticated]
    queryset = Placement.inactive_objects.all()
    serializer_class = PlacementBaseDetailSerializer


class InactivePlacementRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerPlacement, IsAuthenticated]
    serializer_class = PlacementSerializer

    def get_object(self):
        placement = get_object_or_404(Placement.inactive_objects, pk=self.kwargs['pk'])

        self.check_object_permissions(self.request, placement)

        return placement

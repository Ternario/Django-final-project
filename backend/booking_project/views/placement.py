from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import  IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from booking_project.permissions import *
from booking_project.serializers.placement import *


class PlacementCreateView(CreateAPIView):
    permission_classes = [IsLandLord]
    queryset = Placement.objects.all()
    serializer_class = CreatePlacementSerializer


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
        params = self.request.query_params.get('city')

        if params:
            return Placement.objects.filter(placement_location__city=params, is_active=True)
        else:
            return Placement.objects.filter(is_active=True)


class PlacementRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerPlacement, IsAuthenticatedOrReadOnly]
    queryset = Placement.objects.all()
    serializer_class = PlacementSerializer
    lookup_field = 'pk'


class InactivePlacementListView(ListAPIView):
    permission_classes = [IsOwnerPlacement]
    queryset = Placement.objects.filter(is_active=False)
    serializer_class = PlacementBaseDetailSerializer


class InactivePlacementRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerPlacement, IsAuthenticatedOrReadOnly]
    queryset = Placement.objects.all()
    serializer_class = PlacementSerializer
    lookup_field = 'pk'

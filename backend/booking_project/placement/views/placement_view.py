from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny

from booking_project.permissions import *
from booking_project.placement.serializers.placement_serializer import *


class PlacementCreateView(CreateAPIView):
    permission_classes = [IsLandLord, IsAuthenticated]
    queryset = Placement.objects.all()
    serializer_class = FullPlacementSerializer


class PlacementListView(ListAPIView):
    permission_classes = [AllowAny]
    queryset = Placement.objects.all()
    serializer_class = PlacementBaseDetailSerializer


class PlacementRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerPlacement, IsAuthenticatedOrReadOnly]
    queryset = Placement.objects.all()
    serializer_class = PlacementSerializer
    lookup_field = 'pk'


class PlacementDetailsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerPlacementDetails, IsAuthenticatedOrReadOnly]
    queryset = PlacementDetails.objects.all()
    serializer_class = PlacementDetailSerializer
    lookup_field = 'placement'


class LocationRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerPlacementDetails, IsAuthenticatedOrReadOnly]
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    lookup_field = 'placement'

from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from booking_project.permissions import IsOwnerPlacementDetails
from booking_project.placement.models.location import Location
from booking_project.placement.serializers.location_serializer import LocationSerializer


class LocationRetrieveUpdateDestroyView(RetrieveUpdateAPIView):
    permission_classes = [IsOwnerPlacementDetails, IsAuthenticatedOrReadOnly]
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    lookup_field = 'placement'

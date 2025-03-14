from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from booking_project.permissions import IsOwnerPlacementDetails
from booking_project.models.placement_location import PlacementLocation
from booking_project.serializers.placement_location import LocationSerializer


class LocationRetrieveUpdateView(RetrieveUpdateAPIView):
    permission_classes = [IsOwnerPlacementDetails, IsAuthenticatedOrReadOnly]
    queryset = PlacementLocation.objects.all()
    serializer_class = LocationSerializer
    lookup_field = 'placement'

from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from booking_project.permissions import IsOwnerPlacementDetails
from booking_project.placement.models.placement_details import PlacementDetails
from booking_project.placement.serializers.placement_details_serializer import PlacementDetailSerializer


class PlacementDetailsRetrieveUpdateDestroyView(RetrieveUpdateAPIView):
    permission_classes = [IsOwnerPlacementDetails, IsAuthenticatedOrReadOnly]
    queryset = PlacementDetails.objects.all()
    serializer_class = PlacementDetailSerializer
    lookup_field = 'placement'

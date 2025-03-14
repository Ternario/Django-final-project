from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from booking_project.permissions import IsOwnerPlacementDetails
from booking_project.models.placement_details import PlacementDetails
from booking_project.serializers.placement_details import PlacementDetailSerializer


class PlacementDetailsRetrieveUpdateView(RetrieveUpdateAPIView):
    permission_classes = [IsOwnerPlacementDetails, IsAuthenticatedOrReadOnly]
    serializer_class = PlacementDetailSerializer

    def get_object(self):
        placement_details = get_object_or_404(PlacementDetails, placement=self.kwargs['placement'])

        self.check_object_permissions(self.request, placement_details.placement.owner)

        return placement_details

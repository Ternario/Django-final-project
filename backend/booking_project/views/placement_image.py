from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from booking_project.permissions import IsOwnerPlacementDetails
from booking_project.models.placement_image import PlacementImage
from booking_project.serializers.placement_image import PlacementImageSerializer


class ImageListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsOwnerPlacementDetails, IsAuthenticatedOrReadOnly]
    queryset = PlacementImage.objects.all()
    serializer_class = PlacementImageSerializer


class ImageRetrieveUpdateAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerPlacementDetails, IsAuthenticatedOrReadOnly]
    queryset = PlacementImage.objects.all()
    serializer_class = PlacementImageSerializer
    lookup_field = 'placement'

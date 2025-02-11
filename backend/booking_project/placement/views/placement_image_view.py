from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from booking_project.permissions import IsOwnerPlacementDetails
from booking_project.placement.models.placement_image import PlacementImage
from booking_project.placement.serializers.placement_image_serializer import PlacementImageSerializer


class ImageListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsOwnerPlacementDetails, IsAuthenticatedOrReadOnly]
    queryset = PlacementImage.objects.all()
    serializer_class = PlacementImageSerializer


class ImageRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = [IsOwnerPlacementDetails, IsAuthenticatedOrReadOnly]
    queryset = PlacementImage.objects.all()
    serializer_class = PlacementImageSerializer
    lookup_field = 'placement'

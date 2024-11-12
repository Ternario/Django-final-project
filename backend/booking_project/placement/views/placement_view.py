from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.permissions import AllowAny

from booking_project.placement.models.placement import Placement
from booking_project.placement.serializers.placement_serializer import PlacementSerializer


class PlacementView(RetrieveAPIView):
    queryset = Placement.objects.all()
    serialize_class = PlacementSerializer


class PlacementCreateView(CreateAPIView):
    permission_classes = [AllowAny]

    queryset = Placement.objects.all()
    serializer_class = PlacementSerializer

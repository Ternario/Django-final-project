from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView, ListCreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from booking_project.placement.models.location import Location
from booking_project.placement.models.placement import Placement
from booking_project.placement.serializers.placement_serializer import PlacementSerializer, LocationSerializer, \
    PlacementDetailSerializer, FullPlacementSerializer


class PlacementView(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Placement.objects.all()
    serializer_class = FullPlacementSerializer


class PlacementCreateView(CreateAPIView):
    permission_classes = [AllowAny]

    queryset = Placement.objects.all()
    serializer_class = FullPlacementSerializer

    # def create(self, request, *args, **kwargs):
    #     serializer = FullPlacementSerializer(data=request.data)
    #     if serializer.is_valid(raise_exception=True):
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

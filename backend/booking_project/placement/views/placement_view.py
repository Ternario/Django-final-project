from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from booking_project.permissions import IsLandLord, IsOwnerPlacement, IsOwnerPlacementDetails
from booking_project.placement.models.location import Location
from booking_project.placement.models.placement import Placement
from booking_project.placement.models.placement_details import PlacementDetails
from booking_project.placement.serializers.placement_serializer import PlacementSerializer, LocationSerializer, \
    PlacementDetailSerializer, FullPlacementSerializer


class PlacementCreateView(CreateAPIView):
    permission_classes = [IsLandLord, IsAuthenticated]
    queryset = Placement.objects.all()
    serializer_class = FullPlacementSerializer


class PlacementDestroyView(DestroyAPIView):
    permission_classes = [IsOwnerPlacement, IsLandLord, IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        try:
            placement = Placement.objects.get(pk=request.data.get('id'))
            placement.delete()
            return Response({
                "detail": "Placement was deleted successfully"
            }, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"detail": "Placement not found"}, status=status.HTTP_400_BAD_REQUEST)


class PlacementRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerPlacement, IsLandLord, IsAuthenticatedOrReadOnly]
    queryset = Placement.objects.all()
    serializer_class = PlacementSerializer

    def update(self, request, *args, **kwargs):
        placement = Placement.objects.get(pk=request.data.get('id'))

        serializer = self.serializer_class(placement, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlacementDetailsRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerPlacementDetails, IsLandLord, IsAuthenticatedOrReadOnly]
    queryset = PlacementDetails.objects.all()
    serializer_class = PlacementDetailSerializer

    def update(self, request, *args, **kwargs):
        placement_detail = PlacementDetails.objects.get(pk=request.data.get('id'))

        serializer = self.serializer_class(placement_detail, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LocationRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwnerPlacementDetails, IsLandLord, IsAuthenticatedOrReadOnly]
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def update(self, request, *args, **kwargs):
        location = Location.objects.get(pk=request.data.get('id'))

        serializer = self.serializer_class(location, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

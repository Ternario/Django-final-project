from rest_framework.generics import UpdateAPIView, ListCreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from booking_project.serializers.booking_details import *
from booking_project.permissions import IsOwnerBookingPlacement, IsLandLord, IsOwnerBooking
from booking_project.models.placement import Placement


class BookingDetailsOwnerList(ListAPIView):
    permission_classes = [IsLandLord, IsAuthenticated]
    serializer_class = BookingDetailSerializer

    def get_queryset(self):
        user = self.request.user
        placements = Placement.objects.filter(owner=user, is_active=True)
        if not placements:
            return []

        return BookingDetails.objects.filter(placement__in=placements, is_active=True)


class BookingDetailsUserListCreate(ListCreateAPIView):
    permission_classes = [IsOwnerBooking, IsAuthenticated]
    serializer_class = BookingDetailSerializer

    def get_queryset(self):
        if self.request.method == 'GET':
            user = self.request.user
            return BookingDetails.objects.filter(user=user, is_active=True)
        else:
            return BookingDetails.objects.all()


class InactiveBookingDetailsUserCreate(ListAPIView):
    permission_classes = [IsOwnerBooking, IsAuthenticated]
    serializer_class = BookingDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return BookingDetails.objects.filter(user=user, is_active=False)


class InactiveBookingDetailsOwnerCreate(ListAPIView):
    permission_classes = [IsOwnerBookingPlacement, IsLandLord, IsAuthenticated]
    serializer_class = BookingDetailSerializer

    def get_queryset(self):
        user = self.request.user
        placements = Placement.objects.filter(owner=user, is_active=True)
        if not placements:
            return []

        return BookingDetails.objects.filter(placement__in=placements, is_active=False)


class BookingDetailsOwnerUpdateView(UpdateAPIView):
    permission_classes = [IsOwnerBookingPlacement, IsLandLord, IsAuthenticated]
    serializer_class = BookingDetailsOwnerSerializer
    queryset = BookingDetails.objects.all()
    lookup_field = 'pk'


class BookingDetailsUserUpdateView(UpdateAPIView):
    permission_classes = [IsOwnerBooking, IsAuthenticated]
    serializer_class = BookingDetailsUserSerializer
    queryset = BookingDetails.objects.all()
    lookup_field = 'pk'

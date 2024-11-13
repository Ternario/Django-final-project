from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from booking_project.permissions import IsLandLord
from booking_project.booking_info.serializers.booking_details_serializer import BookingDatesCreateSerializer


class BookingDatesListCreate(CreateAPIView):
    permission_classes = [IsLandLord, IsAuthenticated]
    # permission_classes = [AllowAny]
    serializer_class = BookingDatesCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

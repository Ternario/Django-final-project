from rest_framework import status
from rest_framework.generics import UpdateAPIView, ListCreateAPIView
from rest_framework.response import Response

from booking_project.booking_info.serializers.booking_details_serializer import *


class BookingDetailsListCreate(ListCreateAPIView):
    queryset = BookingDetails.objects.all()
    serializer_class = BookingDetailSerializer

    def get_queryset(self):
        if self.request.method == 'GET':
            user = self.request.user
            return BookingDetails.objects.filter(user=user)
        else:
            return self.queryset


class BookingDetailsOwnerUpdateView(UpdateAPIView):
    serializer_class = BookingDetailsOwnerSerializer
    queryset = BookingDetails.objects.all()

    def update(self, request, *args, **kwargs):
        booking = BookingDetails.objects.get(pk=request.data.get('id'))
        serializer = self.get_serializer(booking, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookingDetailsUserUpdateView(UpdateAPIView):
    serializer_class = BookingDetailsUserSerializer
    queryset = BookingDetails.objects.all()

    def update(self, request, *args, **kwargs):
        booking = BookingDetails.objects.get(pk=request.data.get('id'))
        serializer = self.get_serializer(booking, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

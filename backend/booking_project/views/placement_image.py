from rest_framework import status, serializers
from rest_framework.generics import CreateAPIView, get_object_or_404, GenericAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response

from booking_project.models import Placement
from booking_project.permissions import IsOwnerPlacementImages
from booking_project.models.placement_image import PlacementImage
from booking_project.serializers.placement import PlacementActivationSerializer
from booking_project.serializers.placement_image import (
    PlacementImageSerializer, PlacementImageFirstCreateSerializer, PlacementImageDestroySerializer
)


class ImageFirstCreateAPIView(CreateAPIView):
    permission_classes = [IsOwnerPlacementImages, IsAuthenticated]
    serializer_class = PlacementImageFirstCreateSerializer

    def create(self, request, *args, **kwargs):
        placement = Placement.all_objects.get(pk=self.kwargs['placement'])
        activate_value = request.data.get('activate', False)

        image_serializer = self.get_serializer(data=request.data, context={'placement': placement})

        if image_serializer.is_valid(raise_exception=True):
            data = image_serializer.save()
            response_data = {'uploaded_images': data}

        else:
            return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if activate_value == 'True':
            activation_serializer = PlacementActivationSerializer(data={'activate': activate_value}, instance=placement)

            try:
                activation_serializer.is_valid(raise_exception=True)
                data = activation_serializer.save()
                response_data['activate'] = data

            except serializers.ValidationError as e:
                response_data['activate'] = str(e.detail['activate'][0])

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(data, status=status.HTTP_201_CREATED)


class ImageListDestroyAPIView(GenericAPIView, ListModelMixin):
    permission_classes = [IsOwnerPlacementImages, IsAuthenticatedOrReadOnly]
    queryset = PlacementImage.objects.all()
    serializer_class = PlacementImageSerializer
    delete_serializer_class = PlacementImageDestroySerializer

    def get_serializer_class(self):
        if self.request.method == 'DELETE':
            return self.delete_serializer_class
        return self.serializer_class

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            deleted_count = serializer.delete_images()

            return Response({"detail": f"{deleted_count} images deleted"}, status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

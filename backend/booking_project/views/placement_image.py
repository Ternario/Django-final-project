from rest_framework import status, serializers
from rest_framework.generics import CreateAPIView, get_object_or_404, ListCreateAPIView, DestroyAPIView
from rest_framework.response import Response

from booking_project.models import Placement
from booking_project.permissions import IsOwnerPlacementRelatedModels, IsOwnerPlacement
from booking_project.models.placement_image import PlacementImage
from booking_project.serializers.placement import PlacementActivationSerializer
from booking_project.serializers.placement_image import PlacementImageSerializer


class ImageFirstCreateAPIView(CreateAPIView):
    """
    View to create Placement Images of placement by id only for owner user.

    Example of POST request:
    POST /placement/1/images/

    {
        'activate': 'True'
        'uploaded_images': [image4, image5, image6]
    }

    Response:
    {
        'activate': 'Announcement successfully activated.'
        'uploaded_images': [image4, image5, image6]
    }

    Permissions:
         - IsLandLord: can only be used by users who are landlords.
         - OnlyOwnerPlacement: can only be used by the owner of the Placement.
         - IsAuthenticated: can only be used by an authorized user.
    """

    permission_classes = [IsOwnerPlacement]
    serializer_class = PlacementImageSerializer

    def create(self, request, *args, **kwargs):
        placement = get_object_or_404(Placement.all_objects, pk=self.kwargs['placement'])
        activate_value = request.data.get('activate', False)

        image_serializer = self.get_serializer(data=request.data,
                                               context={'placement': placement, 'request': self.request})

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


class ImageListDestroyAPIView(ListCreateAPIView, DestroyAPIView):
    """
    View to get, create and destroy Placement Images of placement by id only for owner user.

    Example of GET request:
    GET /placement/1/images/

    Response:
    {
        'images': [image1, image2, image3]
    }

    Example of POST request:
    POST /placement/1/images/

    {
        'uploaded_images': [image4, image5, image6]
    }

    Response:
    {
        'uploaded_images': [image4, image5, image6]
    }

    Example of DELETE request:
    DELETE /placement/1/images/

    {
        'image_list': [1, 2, 3]
    }

    Response:
    {
        'detail': 'Successfully deleted 3 image(s).'
    }

    Permissions:
         - IsLandLord: can only be used by users who are landlords.
         - OnlyOwnerPlacement: can only be used by the owner of the Placement.
         - OnlyOwnerPlacementRelatedModels: can only be used by the owner of the Placement Images.
         - IsAuthenticated: can only be used by an authorized user.
    """

    serializer_class = PlacementImageSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsOwnerPlacement()]

        return [IsOwnerPlacementRelatedModels()]

    def get_queryset(self):
        placement = self.kwargs['placement']

        queryset = PlacementImage.objects.filter(placement=placement)

        return queryset

    def get_filtered_queryset(self, request, filters=None):

        queryset = self.get_queryset()

        if filters:
            queryset = queryset.filter(**filters)

        for obj in queryset:
            self.check_object_permissions(request, obj)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_filtered_queryset(request)

        serializer = self.get_serializer(queryset, many=True)

        return Response({'images': serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):

        placement = get_object_or_404(Placement.all_objects, pk=self.kwargs['placement'])

        self.check_object_permissions(request, placement)

        serializer = self.get_serializer(data=request.data, context={'placement': placement, 'request': self.request})

        if serializer.is_valid(raise_exception=True):
            data = serializer.save()

            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):

        ids_list = self.request.data.get('image_list', None)

        if not ids_list:
            return Response({'detail': 'Image list cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.get_filtered_queryset(request, {'id__in': ids_list})

        if not queryset.exists():
            return Response({'detail': 'No matching images found.'}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = queryset.delete()

        return Response({'detail': f'Successfully deleted {deleted_count} image(s).'},
                        status=status.HTTP_204_NO_CONTENT)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from properties.models import User

from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from properties.permissions import IsLandlord
from properties.models import Location
from properties.serializers import LocationSerializer, LocationCreateSerializer

from properties.utils.check_permissions.related_to_property_models import CheckRelatedPropertyModelsPermission


class LocationCAV(CreateAPIView):
    """
    API view for creating a location associated with a specific property.

    - POST: create a new `Location` object linked to a property identified by `prop_id`
      and landlord `hash_id`.
    - Validates that the requesting user has access to the property using
      `CheckRelatedPropertyModelsPermission`.
    - The location is created using `LocationCreateSerializer` with the property
      reference passed through the serializer context.
    - Only accessible to the property owner, company, or company member (`IsLandlord`).

    This view ensures that only authorized landlords can create or assign
    a location to their property.
    """
    permission_classes = [IsLandlord]
    queryset = Location.objects.all()
    serializer_class = LocationCreateSerializer

    def create(self, request, *args, **kwargs) -> Response:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']
        p_id: int = self.kwargs['p_id']

        CheckRelatedPropertyModelsPermission(user, hash_id, p_id).access()

        serializer: LocationCreateSerializer = self.get_serializer(
            data=self.request.data, context={'property_ref': p_id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LocationRUAV(RetrieveUpdateAPIView):
    """
    API view for retrieving the location associated with a specific property.

    - GET: retrieve the `Location` object linked to a property identified by `id` and landlord `hash_id`.
    - Checks that the requesting user is authorized to access the property using `CheckRelatedPropertyModelsPermission`.
    - Only accessible to the property owner, company, or company member (`IsLandlord`).

    This view ensures that only users with proper access rights can view the location of a property.
    """
    permission_classes = [IsLandlord]
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get_object(self) -> Location:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']
        p_id: int = self.kwargs['p_id']

        CheckRelatedPropertyModelsPermission(user, hash_id, p_id).access()

        return get_object_or_404(self.get_queryset(), property_ref_id=p_id)

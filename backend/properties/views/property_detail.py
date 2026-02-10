from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from properties.models import User

from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from properties.permissions import IsLandlord
from properties.models import PropertyDetail
from properties.serializers import PropertyDetailCreateSerializer, PropertyDetailSerializer

from properties.utils.check_permissions.related_to_property_models import CheckRelatedPropertyModelsPermission


class PropertyDetailCAV(CreateAPIView):
    """
    API view for creating property details associated with a specific property.

    - POST: create a new `PropertyDetail` object linked to a property identified
      by `p_id` and landlord `hash_id`.
    - Validates that the requesting user has access to the property using
      `CheckRelatedPropertyModelsPermission`.
    - The property details are created using `PropertyDetailCreateSerializer`
      with the property reference passed through the serializer context.
    - Only accessible to the property owner, company, or company member (`IsLandlord`).

    This view ensures that only authorized landlords can create details
    for their property.
    """
    permission_classes = [IsLandlord]
    queryset = PropertyDetail.objects.all()
    serializer_class = PropertyDetailCreateSerializer

    def create(self, request, *args, **kwargs) -> Response:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']
        p_id: int = self.kwargs['p_id']

        CheckRelatedPropertyModelsPermission(user, hash_id, p_id).access()

        serializer: PropertyDetailCreateSerializer = self.get_serializer(
            data=self.request.data, context={'property_ref': p_id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PropertyDetailRUAV(RetrieveUpdateAPIView):
    """
    API view for retrieving and updating property details associated
    with a specific property.

    - GET: retrieve the `PropertyDetail` object linked to a property
      identified by `p_id` and landlord `hash_id`.
    - PUT/PATCH: update the property details for the specified property.
    - Validates that the requesting user has access to the property using
      `CheckRelatedPropertyModelsPermission`.
    - Only accessible to the property owner, company, or company member (`IsLandlord`).

    This view ensures that only authorized landlords can view or modify
    the details of their property.
    """
    permission_classes = [IsLandlord]
    queryset = PropertyDetail.objects.all()
    serializer_class = PropertyDetailSerializer

    def get_object(self):
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']
        p_id: int = self.kwargs['p_id']

        CheckRelatedPropertyModelsPermission(user, hash_id, p_id).access()

        return get_object_or_404(self.get_queryset(), peroperty_ref_id=p_id)

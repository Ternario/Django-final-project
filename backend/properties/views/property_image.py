from __future__ import annotations
from typing import List, TYPE_CHECKING

from drf_spectacular.utils import extend_schema

from properties.utils.check_permissions.related_to_property_models import CheckRelatedPropertyModelsPermission

if TYPE_CHECKING:
    from properties.models import User
    from django.db.models import QuerySet

from rest_framework.generics import ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from properties.permissions import IsLandlord
from properties.models import PropertyImage
from properties.serializers import PropertyImageSerializer, PropertyImageDestroySerializer
from properties.utils.decorators import atomic_handel


class PropertyImageLCAV(ListCreateAPIView):
    """
    API view for listing and uploading property images associated with a specific property.

    - GET: retrieve a list of `PropertyImage` objects linked to a property
      identified by `p_id` and landlord `hash_id`.
    - POST: upload one or multiple images for the specified property.
    - Validates that the requesting user has access to the property using
      `CheckRelatedPropertyModelsPermission`.
    - Image validation (size, format, and limits per property) is handled
      by `PropertyImageSerializer` and its custom `ListSerializer`.
    - The property reference is passed through the serializer context.
    - Only accessible to the property owner, company, or company member (`IsLandlord`).

    This view ensures that only authorized landlords can manage
    images for their property.
    """
    permission_classes = [IsLandlord]
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer

    def get_queryset(self) -> QuerySet[PropertyImage]:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']
        p_id: int = self.kwargs['p_id']

        CheckRelatedPropertyModelsPermission(user, hash_id, p_id).access()

        return super().get_queryset().filter(property_ref_id=p_id, property_ref__owner__hash_id=hash_id)

    def create(self, request, *args, **kwargs) -> Response:
        p_id: str = self.kwargs['p_id']

        serializer: PropertyImageSerializer = self.get_serializer(
            data=self.request.data,
            context={'property_ref': p_id, 'request': self.request},
            many=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PropertyImageDestroyAV(APIView):
    """
    API view for deleting one or multiple property images associated
    with a specific property.

    - DELETE: remove multiple `PropertyImage` objects by a list of image IDs.
    - Validates that the requesting user has access to the property using
      `CheckRelatedPropertyModelsPermission`.
    - Ensures that all provided image IDs belong to the specified property
      through `PropertyImageDestroySerializer`.
    - Deletion is wrapped in a database transaction (`atomic_handel`)
      to ensure consistency.
    - Only accessible to the property owner, company, or company member (`IsLandlord`).

    This view ensures that only authorized landlords can delete
    images belonging to their property.
    """
    permission_classes = [IsLandlord]

    @extend_schema(
        request=PropertyImageDestroySerializer,
        responses={204: None},
        description='Delete image/list of images.'
    )
    @atomic_handel
    def delete(self, request, *args, **kwargs) -> Response:
        user: User = self.request.user
        hash_id: str = self.kwargs['hash_id']
        p_id: int = self.kwargs['p_id']

        CheckRelatedPropertyModelsPermission(user, hash_id, p_id).access()

        serializer: PropertyImageDestroySerializer = PropertyImageDestroySerializer(
            data=self.request.data, context={'property_ref': p_id}
        )
        serializer.is_valid(raise_exception=True)
        ids: List[int] = serializer.validated_data['image_ids']

        PropertyImage.objects.filter(id__in=ids).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

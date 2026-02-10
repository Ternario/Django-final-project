from typing import TYPE_CHECKING, Type

from django_filters.rest_framework import DjangoFilterBackend

if TYPE_CHECKING:
    from rest_framework.serializers import Serializer

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from properties.models import DeletionLog
from properties.serializers import DeletionLogSerializer, DeletionLogBaseDetailSerializer


class DeletionLogMVS(ModelViewSet):
    """
    ViewSet for managing DeletionLog resources.

    Provides list, retrieve, create, update, and delete actions.
    - All actions are accessible to site admins only.
    - Uses DeletionLogBaseDetailSerializer for list view,
      and DeletionLogSerializer for other actions.
    """
    permission_classes = [IsAdminUser]
    queryset = DeletionLog.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['deleted_by', 'deleted_by_token', 'deleted_model_name', 'deleted_object_id', 'deletion_type',
                        'deleted_at']

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == 'list':
            return DeletionLogBaseDetailSerializer
        else:
            return DeletionLogSerializer

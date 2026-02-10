from rest_framework.serializers import ModelSerializer

from properties.models import DeletionLog
from properties.serializers.user import UserBaseSerializer


class DeletionLogBaseDetailSerializer(ModelSerializer):
    class Meta:
        model = DeletionLog
        fields = ['id', 'deleted_by', 'deleted_model_name', 'deleted_object_id', 'deletion_type']


class DeletionLogSerializer(ModelSerializer):
    deleted_by = UserBaseSerializer(read_only=True)

    class Meta:
        model = DeletionLog
        fields = '__all__'

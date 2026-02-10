from rest_framework.serializers import ModelSerializer

from properties.models import CancellationPolicy


class CancellationPolicyBaseSerializer(ModelSerializer):
    class Meta:
        model = CancellationPolicy
        fields = ['id', 'name', 'type']


class CancellationPolicySerializer(ModelSerializer):
    class Meta:
        model = CancellationPolicy
        exclude = ['created_at', 'updated_at']

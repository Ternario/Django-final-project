from rest_framework.serializers import ModelSerializer

from properties.models import PropertySlugHistory


class PropertySlugHistorySerializer(ModelSerializer):
    class Meta:
        model = PropertySlugHistory
        fields = '__all__'

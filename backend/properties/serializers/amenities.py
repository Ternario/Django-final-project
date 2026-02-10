from typing import Dict, Any

from rest_framework.serializers import ModelSerializer

from properties.models import AmenityCategory, Amenity


class AmenitySerializer(ModelSerializer):
    class Meta:
        model = Amenity
        exclude = ['created_at', 'updated_at']


class AmenityCategorySerializer(ModelSerializer):
    amenities = AmenitySerializer(many=True, read_only=True)

    class Meta:
        model = AmenityCategory
        exclude = ['created_at', 'updated_at']

    def to_representation(self, instance: AmenityCategory):
        data: Dict[str, Any] = super().to_representation(instance)
        data['amenities'] = sorted(data['amenities'], key=lambda x: x['name'])
        return data

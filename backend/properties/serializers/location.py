from __future__ import annotations

from typing import Any, Dict

from rest_framework.serializers import ModelSerializer

from properties.models import Location, Region
from properties.services.location.compare_data import CompareLocationData
from properties.utils.constants.location import fields


class LocationCreateSerializer(ModelSerializer):
    class Meta:
        model = Location
        exclude = ['created_at', 'updated_at']
        read_only_fields = ['property_ref', 'latitude', 'longitude']

    def create(self, validated_data: Dict[str, Any]) -> Location:
        property_ref: int = self.context['property_ref']

        match_location: CompareLocationData = CompareLocationData(**validated_data)
        result: Dict[str, Any] = match_location.compare()

        if result.get('region', None):
            region_obj = Region.objects.create(name=result['region'], country=validated_data['country'])
            result['region'] = region_obj

        result['country'] = validated_data['country']

        lookup: Dict[str, str] = {
            'city': result.pop('city'),
            'post_code': result.pop('post_code'),
            'street_address': result.pop('street_address'),
            'house_number': result.pop('house_number'),
        }

        return Location.objects.create(**lookup, property_ref_id=property_ref, defaults=result)


class LocationPublicSerializer(ModelSerializer):
    class Meta:
        model = Location
        exclude = ['latitude', 'longitude', 'created_at', 'updated_at']


class LocationSerializer(ModelSerializer):
    class Meta:
        model = Location
        exclude = ['created_at', 'updated_at']
        read_only_fields = ['property_ref']

    def update(self, instance: Location, validated_data: Dict[str, Any]) -> Location:
        new_data: Dict[str, Any] = {field: validated_data.get(field, getattr(instance, field)) for field in fields}

        match_location: CompareLocationData = CompareLocationData(**new_data)
        result: Dict[str, str | float] = match_location.compare()

        for attr, value in result.items():
            if hasattr(instance, attr) and value != getattr(instance, attr):
                setattr(instance, attr, value)

        instance.save()

        return instance

from rest_framework import serializers

from booking_project.placement.models.location import Location
from booking_project.placement.models.placement import Placement
from booking_project.placement.models.placement_details import PlacementDetails


class PlacementDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementDetails
        exclude = ['placement']
        read_only_fields = ['created_at', 'updated_at', 'placement']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        exclude = ['placement']
        read_only_fields = ['created_at', 'updated_at', "placement"]


class PlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placement
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'owner']


class FullPlacementSerializer(serializers.ModelSerializer):
    placement_details = PlacementDetailSerializer(write_only=True, partial=True)
    placement_location = LocationSerializer(write_only=True, partial=True)

    class Meta:
        model = Placement
        fields = '__all__'
        only_read_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        details_field = validated_data.pop('placement_details')

        location = validated_data.pop('placement_location')

        placement = Placement.objects.create(**validated_data)
        placement.save()

        PlacementDetails.objects.create(placement=placement, **details_field)

        Location.objects.create(placement=placement, **location)

        return placement

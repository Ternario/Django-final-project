from rest_framework import serializers

from booking_project.placement.models.location import Location
from booking_project.placement.models.placement import Placement
from booking_project.placement.models.placement_details import PlacementDetails


class PlacementDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementDetails
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'placement']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
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
        only_read_fields = ['created_at', 'updated_at', 'is_deleted']

    def create(self, validated_data):
        details_field = validated_data.pop('placement_details', None)

        location = validated_data.pop('placement_location', None)

        placement = Placement.objects.create(**validated_data)
        placement.save()

        if details_field:
            PlacementDetails.objects.create(placement=placement, **details_field)

        Location.objects.create(placement=placement, **location)

        return placement


class PlacementBaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placement
        exclude = ['is_active', 'owner', 'is_deleted']

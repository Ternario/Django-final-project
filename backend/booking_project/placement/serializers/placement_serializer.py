from rest_framework import serializers

from booking_project.placement.models.location import Location
from booking_project.placement.models.placement import Placement
from booking_project.placement.models.placement_details import PlacementDetails


class PlacementDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementDetails
        # fields = '__all__'
        exclude = ['placement']
        read_only_fields = ['created_at', 'updated_at']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        # fields = '__all__'
        exclude = ['placement']
        read_only_fields = ['created_at', 'updated_at']


class PlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placement
        fields = '__all__'


class FullPlacementSerializer(serializers.ModelSerializer):
    placement_details = PlacementDetailSerializer(write_only=True)
    placement_location = LocationSerializer(write_only=True)

    class Meta:
        model = Placement
        fields = '__all__'
        only_read_fields = ['created_at', 'updated_at', 'number_of_reviews']

    def create(self, validated_data):
        details_field = validated_data.pop('placement_details')

        location = validated_data.pop('placement_location')

        placement = Placement.objects.create(**validated_data)
        placement.save()

        PlacementDetails.objects.create(placement=placement, **details_field)

        Location.objects.create(placement=placement, **location)

        return placement

from rest_framework import serializers

from booking_project.placement.models.booking_dates import BookingDates
from booking_project.placement.models.location import Location
from booking_project.placement.models.placement import Placement
from booking_project.placement.models.placement_details import PlacementDetails


class PlacementDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementDetails
        exclude = ['placement_id']
        read_only_fields = ['created_at', 'updated_at']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        exclude = ['placement_id']


class PlacementSerializer(serializers.ModelSerializer):
    placement_details = PlacementDetailSerializer()
    location_details = LocationSerializer()

    class Meta:
        model = Placement
        fields = '__all__'
        only_read_fields = ['created_at', 'updated_at', 'number_of_reviews']

    def create(self, validated_data):
        details_field = validated_data.pop('placement_details')
        location = validated_data.pop('location_details')
        instance = Placement.objects.create(**validated_data)
        PlacementDetails.objects.create(placement_id=instance, **details_field)
        Location.objects.create(placement_id=instance, **location)

        return instance


class BookingDatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDates
        fields = '__all__'

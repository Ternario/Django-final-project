from rest_framework import serializers

from booking_project.models.placement_location import PlacementLocation


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementLocation
        exclude = ['id', 'created_at', 'updated_at']
        read_only_fields = ['placement']

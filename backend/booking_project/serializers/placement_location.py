from rest_framework import serializers

from booking_project.models.placement_location import PlacementLocation


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementLocation
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', "placement"]

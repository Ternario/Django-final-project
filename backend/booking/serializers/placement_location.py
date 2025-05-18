from rest_framework import serializers

from booking.models.placement_location import PlacementLocation


class PlacementLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementLocation
        exclude = ['id', 'created_at', 'updated_at']
        read_only_fields = ['placement']

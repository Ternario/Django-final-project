from rest_framework import serializers

from booking_project.models.placement_details import PlacementDetails


class PlacementDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementDetails
        exclude = ['id', 'created_at', 'updated_at']
        read_only_fields = ['placement']
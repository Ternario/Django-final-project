from rest_framework import serializers

from booking_project.models.placement_details import PlacementDetails


class PlacementDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementDetails
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'placement']

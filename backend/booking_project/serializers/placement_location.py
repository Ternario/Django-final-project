from rest_framework import serializers

from booking_project.models.placement_location import Location


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', "placement"]

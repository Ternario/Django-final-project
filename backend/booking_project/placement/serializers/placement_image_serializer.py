from rest_framework import serializers

from booking_project.placement.models.placement_image import PlacementImage


class PlacementImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementImage
        fields = '__all__'

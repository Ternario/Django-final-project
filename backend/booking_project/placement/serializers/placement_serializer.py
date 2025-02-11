from django.db.models import Avg
from rest_framework import serializers

from booking_project.placement.models.location import Location
from booking_project.placement.models.placement import Placement
from booking_project.placement.models.placement_details import PlacementDetails
from booking_project.placement.models.placement_image import PlacementImage
from booking_project.placement.serializers.location_serializer import LocationSerializer
from booking_project.placement.serializers.placement_details_serializer import PlacementDetailSerializer
from booking_project.placement.serializers.placement_image_serializer import PlacementImageSerializer
from booking_project.reviews.models.review import Review


class PlacementSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField('avg_rating')
    placement_details = serializers.SerializerMethodField('details')
    placement_location = serializers.SerializerMethodField('location')
    placement_images = PlacementImageSerializer(many=True)

    class Meta:
        model = Placement
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'owner', 'rating', 'city', 'rating',
                            'placement_images', 'placement_details']

    def details(self, obj):
        return PlacementDetailSerializer(PlacementDetails.objects.get(placement=obj.pk)).data

    def location(self, obj):
        return LocationSerializer(Location.objects.get(placement=obj.pk)).data

    def avg_rating(self, obj):
        count = Review.objects.filter(placement=obj).aggregate(Avg('rating'))
        return count['rating__avg'] if count['rating__avg'] else 0


class CreatePlacementSerializer(serializers.ModelSerializer):
    placement_details = PlacementDetailSerializer(write_only=True, required=False)
    placement_location = LocationSerializer(write_only=True, required=False)

    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=True),
        write_only=True
    )

    class Meta:
        model = Placement
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'is_deleted']

    def create(self, validated_data):
        details_field = validated_data.pop('placement_details', None)
        location = validated_data.pop('placement_location', None)
        uploaded_images = validated_data.pop('uploaded_images', None)

        if not details_field or location:
            validated_data['is_active'] = False

        placement = Placement.objects.create(**validated_data)
        placement.save()

        if details_field:
            PlacementDetails.objects.create(placement=placement, **details_field)
        else:
            PlacementDetails.objects.create(placement=placement)

        if uploaded_images:
            [PlacementImage.objects.create(placement=placement, placement_image=image) for image in uploaded_images]

        if location:
            Location.objects.create(placement=placement, **location)

        return placement


class PlacementBaseDetailSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField('get_city')
    placement_images = PlacementImageSerializer(many=True)
    rating = serializers.SerializerMethodField('avg_rating')

    def get_city(self, obj):
        city = Location.objects.get(placement=obj.pk)
        return city.city

    def avg_rating(self, obj):
        count = Review.objects.filter(placement=obj).aggregate(Avg('rating'))
        return count['rating__avg'] if count['rating__avg'] else 0

    class Meta:
        model = Placement
        exclude = ['is_active', 'owner', 'is_deleted']

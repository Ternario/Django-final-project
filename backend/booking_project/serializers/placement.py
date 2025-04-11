import re

from django.db.models import Avg
from rest_framework import serializers

from booking_project.models import PlacementImage, Category
from booking_project.models.placement_location import PlacementLocation
from booking_project.models.placement import Placement
from booking_project.models.placement_details import PlacementDetails
from booking_project.serializers.placement_location import LocationSerializer
from booking_project.serializers.placement_details import PlacementDetailSerializer
from booking_project.serializers.placement_image import PlacementImageSerializer
from booking_project.models.review import Review


class PlacementCreateSerializer(serializers.ModelSerializer):
    placement_location = LocationSerializer(write_only=True, required=True)

    class Meta:
        model = Placement
        exclude = ['updated_at', 'is_active', 'is_deleted']
        read_only_fields = ['owner']

    def create(self, validated_data):
        user = self.context['user']
        location = validated_data.pop('placement_location', None)

        placement = Placement.objects.create(owner=user, **validated_data)

        PlacementLocation.objects.create(placement=placement, **location)

        PlacementDetails.objects.create(placement=placement)

        return placement

    def validate(self, attrs):
        total_beds = attrs.get('total_beds')
        single_bed = attrs.get('single_bed')
        double_bed = attrs.get('double_bed')
        post_code = attrs['placement_location'].get('post_code')

        if single_bed == 0 and double_bed == 0:
            raise serializers.ValidationError('Both bed fields can\'t be zero.')

        if total_beds != single_bed + double_bed:
            raise serializers.ValidationError('Both bed fields must be equal to the total beds.')

        if post_code and not re.match('^[0-9]{5}$', post_code):
            raise serializers.ValidationError({'post_code': 'Invalid postal code.'})

        return attrs


class PlacementActivationSerializer(serializers.Serializer):
    activate = serializers.BooleanField(required=False, default=False)

    def update(self, instance, validated_data):

        if validated_data['activate']:
            instance.is_active = True
            instance.save()
            return 'Announcement successfully activated.'

        instance.is_active = False
        instance.save()

        return 'Announcement successfully deactivated.'

    def validate_activate(self, value):
        if value and not self.check_activation_requirements():
            raise serializers.ValidationError('You need to fill in the placement details or add photos.')
        else:
            return value

    def check_activation_requirements(self):
        placement_details = getattr(self.instance, 'placement_details', None)

        if not any(field for field in vars(placement_details).values() if isinstance(field, bool)):
            return False

        if not PlacementImage.objects.filter(placement=self.instance).exists():
            return False

        return True


class PlacementBaseDetailsSerializer(serializers.ModelSerializer):
    city = serializers.SerializerMethodField('get_city')
    placement_image = PlacementImageSerializer(many=True)
    rating = serializers.SerializerMethodField('avg_rating')

    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Placement
        exclude = ['is_active', 'owner', 'is_deleted', 'updated_at', 'category']

    def get_city(self, obj):
        city = PlacementLocation.objects.get(placement=obj.pk)
        return city.city

    def avg_rating(self, obj):
        count = Review.objects.filter(placement=obj).aggregate(Avg('rating'))
        return count['rating__avg'] if count['rating__avg'] else 0


class PlacementAllDetailsSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField('avg_rating')
    placement_details = serializers.SerializerMethodField('details')
    placement_location = serializers.SerializerMethodField('location')
    placement_image = PlacementImageSerializer(many=True, read_only=True)

    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Placement
        exclude = ['owner', 'is_active', 'is_deleted']
        read_only_fields = ['created_at', 'updated_at', 'rating', 'placement_image', 'placement_location',
                            'placement_details', 'id']

    def details(self, obj):
        return PlacementDetailSerializer(PlacementDetails.objects.get(placement=obj.pk)).data

    def location(self, obj):
        return LocationSerializer(PlacementLocation.objects.get(placement=obj.pk)).data

    def avg_rating(self, obj):
        count = Review.objects.filter(placement=obj).aggregate(Avg('rating'))
        return count['rating__avg'] if count['rating__avg'] else 0


class PlacementSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(write_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Placement
        exclude = ['owner', 'is_active', 'is_deleted']
        read_only_fields = ['created_at', 'updated_at', 'id']

    def validate(self, attrs):
        total_beds = attrs.get('total_beds')
        single_bed = attrs.get('single_bed')
        double_bed = attrs.get('double_bed')

        if single_bed == 0 and double_bed == 0:
            raise serializers.ValidationError('Both bed fields can\'t be zero.')

        if total_beds != single_bed + double_bed:
            raise serializers.ValidationError('Both bed fields must be equal to the total beds.')

        return attrs

    def validate_category(self, value):
        try:
            category = Category.objects.get(pk=value)
        except Category.DoesNotExist:
            raise serializers.ValidationError({'category': 'A category with this ID does not exist.'})

        return category

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

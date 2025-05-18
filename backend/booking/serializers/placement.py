import re

from rest_framework import serializers

from booking.models import PlacementImage, Category
from booking.models.placement_location import PlacementLocation
from booking.models.placement import Placement
from booking.models.placement_details import PlacementDetails

from booking.serializers.placement_location import PlacementLocationSerializer
from booking.serializers.placement_details import PlacementDetailSerializer
from booking.serializers.placement_image import PlacementImageSerializer


class PlacementCreateSerializer(serializers.ModelSerializer):
    placement_location = PlacementLocationSerializer(write_only=True, required=True)

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
    city = serializers.CharField(read_only=True)
    avg_rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    placement_images = PlacementImageSerializer(many=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Placement
        exclude = ['is_active', 'owner', 'is_deleted', 'updated_at', 'category']


class PlacementAllDetailsSerializer(serializers.ModelSerializer):
    avg_rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True)
    placement_details = PlacementDetailSerializer(read_only=True)
    placement_location = PlacementLocationSerializer(read_only=True)
    placement_images = PlacementImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Placement
        exclude = ['owner', 'is_active', 'is_deleted']
        read_only_fields = ['created_at', 'updated_at', 'id']


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

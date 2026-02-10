from __future__ import annotations

from typing import Any, TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from django.core.files.uploadedfile import UploadedFile
    from properties.models import LandlordProfile, Amenity, PaymentType, User
    from decimal import Decimal

from rest_framework.serializers import ModelSerializer, CharField, DictField

from base_config.settings import BASE_CURRENCY

from properties.models import Property
from properties.serializers.location import LocationCreateSerializer, LocationPublicSerializer
from properties.serializers.property_detail import PropertyDetailCreateSerializer, PropertyDetailSerializer
from properties.serializers.property_image import PropertyImageSerializer
from properties.serializers.amenities import AmenitySerializer
from properties.serializers.cancellation_policy import CancellationPolicySerializer
from properties.serializers.payment_type import PaymentTypeSerializer

from properties.utils.decorators import atomic_handel


class PropertyCreateSerializer(ModelSerializer):
    location = LocationCreateSerializer(write_only=True, required=False)
    property_details = PropertyDetailCreateSerializer(write_only=True, required=False)
    uploaded_images = PropertyImageSerializer(write_only=True, many=True, required=False)

    class Meta:
        model = Property
        exclude = ['slug', 'rating', 'review_count', 'approval_status', 'is_deleted', 'deleted_at', 'updated_at']
        read_only_fields = ['created_by']

    @atomic_handel
    def create(self, validated_data: Dict[str, Any]) -> Property:
        location: Dict[str, Any] = validated_data.pop('location', {})
        property_details: Dict[str, Any] = validated_data.pop('property_details', {})
        uploaded_images: Dict[str, List[UploadedFile]] = validated_data.pop('uploaded_images', {})
        created_by: User = self.context['user']
        owner: LandlordProfile = self.context['owner']
        amenities: List[Amenity] = validated_data.pop('amenities')
        payment_type: List[PaymentType] = validated_data.pop('payment_type')

        if owner.default_currency.code != BASE_CURRENCY:
            currency_rate: Decimal = owner.default_currency.rate_to_base

            validated_data['base_price'] *= currency_rate
            validated_data['taxes_fees'] *= currency_rate

        prop: Property = Property.objects.create(owner=owner, created_by=created_by, **validated_data)

        prop.amenities.set(amenities)
        prop.payment_types.set(payment_type)
        prop.save()

        if location:
            location_serializer: LocationCreateSerializer = LocationCreateSerializer(
                data=location,
                context={'property_ref': prop.pk}
            )
            location_serializer.is_valid(raise_exception=True)
            location_serializer.save()

        if property_details:
            property_details_serializer: PropertyDetailCreateSerializer = PropertyDetailCreateSerializer(
                data=property_details,
                context={'property_ref': prop.pk}
            )

            property_details_serializer.is_valid(raise_exception=True)
            property_details_serializer.save()

        if uploaded_images:
            image_serializer: PropertyImageSerializer = PropertyImageSerializer(
                data=uploaded_images,
                context={
                    'request': self.context.get('request'),
                    'property_ref': prop.pk
                }
            )

            image_serializer.is_valid(raise_exception=True)
            image_serializer.save()

        return prop


class PropertyBaseSerializer(ModelSerializer):
    city = CharField(source='location.city', read_only=True)
    property_type = CharField(source='get_property_type_display', read_only=True)
    property_area = CharField(source='details.property_area', read_only=True)
    floor = CharField(source='details.floor', read_only=True)
    total_floors = CharField(source='details.total_floors', read_only=True)
    number_of_rooms = CharField(source='details.number_of_rooms', read_only=True)
    total_beds = CharField(source='details.total_beds', read_only=True)
    single_beds = CharField(source='details.single_beds', read_only=True)
    double_beds = CharField(source='details.double_beds', read_only=True)
    sofa_beds = CharField(source='details.sofa_beds', read_only=True)
    number_of_bathrooms = CharField(source='details.number_of_bathrooms', read_only=True)
    property_images = PropertyImageSerializer(many=True, read_only=True)
    pricing = DictField(read_only=True)

    class Meta:
        model = Property
        fields = ['id', 'title', 'description', 'property_type', 'city', 'rating', 'review_count', 'property_area',
                  'floor', 'total_floors', 'number_of_rooms', 'total_beds', 'single_beds', 'double_beds', 'sofa_beds',
                  'number_of_bathrooms', 'property_images', 'pricing']


class PropertySerializer(ModelSerializer):
    owner_name = CharField(source='owner.name', read_only=True)
    property_type = CharField(source='get_property_type_display', read_only=True)
    location = LocationPublicSerializer(read_only=True)
    amenities = AmenitySerializer(many=True, read_only=True)
    payment_type = PaymentTypeSerializer(many=True, read_only=True)
    property_detail = PropertyDetailSerializer(read_only=True)
    property_images = PropertyImageSerializer(many=True, read_only=True)
    cancellation_days = CharField(source='cancellation_policy.free_cancellation_days', read_only=True)
    cancellation_description = CharField(source='cancellation_policy.description', read_only=True)
    pricing = DictField(read_only=True)

    class Meta:
        model = Property
        exclude = ['slug', 'created_by', 'cancellation_policy', 'status', 'approval_status', 'auto_confirm_bookings',
                   'is_deleted', 'deleted_at', 'created_at', 'updated_at']


class PropertyOwnerBaseSerializer(ModelSerializer):
    property_type = CharField(source='get_property_type_display', read_only=True)

    class Meta:
        model = Property
        fields = ['id', 'title', 'slug', 'property_type']


class PropertyOwnerSerializer(ModelSerializer):
    property_type = CharField(source='get_property_type_display', read_only=True)
    amenities = AmenitySerializer(many=True)
    payment_type = PaymentTypeSerializer(many=True)
    cancellation_policy = CancellationPolicySerializer(read_only=True)
    property_images = PropertyImageSerializer(many=True, read_only=True)
    pricing = DictField(read_only=True)

    class Meta:
        model = Property
        exclude = ['slug', 'updated_at']
        read_only_fields = ['id', 'owner', 'location', 'rating', 'review_count', 'approval_status', 'is_deleted']

    def update(self, instance: Property, validated_data: Dict[str, Any]) -> Property:
        amenities: List[Amenity] = validated_data.pop('amenities', [])
        payment_type: List[PaymentType] = validated_data.pop('payment_type', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if amenities:
            instance.amenities.set(amenities)

        if payment_type:
            instance.payment_types.set(payment_type)

        instance.save()

        return instance

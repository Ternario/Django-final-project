from __future__ import annotations

from typing import Dict, List, Any, Set

from PIL import Image
from django.core.files.uploadedfile import UploadedFile
from rest_framework.fields import ListField, IntegerField
from rest_framework.serializers import ModelSerializer, ValidationError, ListSerializer, Serializer

from properties.models import PropertyImage
from properties.utils.decorators import atomic_handel
from properties.utils.constants.images import MAX_SIZE, ALLOWED_FORMATS, MAX_COUNT, MAX_PER_REQUEST
from properties.utils.error_messages.property_image import PROPERTY_IMAGE_ERRORS


class PropertyImageListSerializer(ListSerializer):
    @atomic_handel
    def create(self, validated_data: List[Dict[str, Any]]) -> List[PropertyImage]:
        property_ref: int = self.context['property_ref']

        created_images: List[PropertyImage] = [PropertyImage.objects.create(
            property_ref_id=property_ref,
            image=item['image']
        ) for item in validated_data]

        return created_images

    def validate(self, attrs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        property_ref: int = self.context['property_ref']
        non_field_errors: List[str] = []

        requested: int = len(attrs)

        if requested > MAX_PER_REQUEST:
            non_field_errors.append(PROPERTY_IMAGE_ERRORS['max_amount'])

        total_images: int = PropertyImage.objects.filter(property_ref_id=property_ref).count()

        allowed: int = MAX_COUNT - total_images

        if allowed <= 0:
            non_field_errors.append(PROPERTY_IMAGE_ERRORS['limit'])

        elif requested > allowed:
            non_field_errors.append(PROPERTY_IMAGE_ERRORS['overlimit'].format(allowed_number=allowed))

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

        return attrs


class PropertyImageSerializer(ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ['id', 'property_ref', 'image']
        read_only_fields = ['property_ref']

        list_serializer_class = PropertyImageListSerializer

    def create(self, validated_data: Dict[str, Any]) -> PropertyImage:
        property_ref: int = self.context.get('property_ref')

        return PropertyImage.objects.create(**validated_data, property_ref_id=property_ref)

    def validate_image(self, image: UploadedFile) -> UploadedFile:
        errors: List[str] = []

        if image.size > MAX_SIZE:
            errors.append(PROPERTY_IMAGE_ERRORS['oversize'])

        with Image.open(image.file) as img:
            if img.format not in ALLOWED_FORMATS:
                errors.append(
                    PROPERTY_IMAGE_ERRORS['invalid_format'].format(formats=', '.join(ALLOWED_FORMATS))
                )

        image.seek(0)

        if errors:
            raise ValidationError({'image': errors})

        return image


class PropertyImageDestroySerializer(Serializer):
    image_ids = ListField(
        child=IntegerField(min_value=1),
        allow_empty=False,
        required=True
    )

    def validate_image_ids(self, value: List[int]) -> List[int]:
        property_ref: int = self.context['property_ref']
        existing_ids: List[int] = PropertyImage.objects.filter(
            property_ref_id=property_ref, id__in=value
        ).values_list('id', flat=True)

        missing: Set[int] = set(value) - set(existing_ids)

        if missing:
            raise ValidationError(f'Images with ids {missing} do not exist or do not belong to this property.')

        return value

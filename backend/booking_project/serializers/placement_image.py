from PIL import Image
from rest_framework import serializers

from booking_project.models import PlacementImage
from booking_project.constants.constants_for_image import MAX_SIZE, ALLOWED_FORMATS


class PlacementImageFirstCreateSerializer(serializers.Serializer):
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False),
        write_only=True,
        required=True
    )

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images')
        placement = self.context['placement']

        created_images = 0

        for image in uploaded_images:
            PlacementImage.objects.create(placement=placement, image=image)
            created_images += 1

        return f'{created_images} image(s) have been successfully added.'

    def validate_uploaded_images(self, uploaded_images):
        placement = self.context['placement']

        if uploaded_images is None:
            raise serializers.ValidationError('This field cannot be empty.')

        if len(uploaded_images) > 15:
            raise serializers.ValidationError('The maximum number of images cannot exceed 15.')

        total_images = PlacementImage.objects.filter(placement=placement).count()

        allowed_number = 15 - total_images

        if allowed_number == 0:
            raise serializers.ValidationError(f'You cannot add new images.')

        if len(uploaded_images) > allowed_number:
            raise serializers.ValidationError(f'You can add only {allowed_number} more image(s)')

        for image in uploaded_images:
            if image.size > MAX_SIZE:
                raise serializers.ValidationError(f'Each image must be smaller than 5 MB.')

            img = Image.open(image)

            if img.format not in ALLOWED_FORMATS:
                raise serializers.ValidationError(
                    f'Image format must be one of the following: {', '.join(ALLOWED_FORMATS)}')

        return uploaded_images


class PlacementImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlacementImage
        fields = '__all__'


class PlacementImageDestroySerializer(serializers.Serializer):
    image_list = serializers.ListField(
        child=serializers.ImageField(),
        required=True,
        write_only=True
    )

    def validate_image_list(self, value):
        if not value:
            raise serializers.ValidationError('Image list cannot be empty.')

        images = PlacementImage.objects.filter(id__in=value)

        if not images.exists():
            raise serializers.ValidationError('No matching images found.')

        user = self.context['request'].user
        unauthorized_images = images.exclude(placement__owner=user)

        if unauthorized_images.exists():
            raise serializers.ValidationError('You can only delete your own images.')

        return value

    def delete_images(self):
        image_list = self.validated_data['image_list']
        deleted_count, _ = PlacementImage.objects.filter(id__in=image_list).delete()

        return f'successfully deleted {deleted_count} image(s).'

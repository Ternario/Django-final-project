from PIL import Image
from rest_framework import serializers

from booking.models import PlacementImage
from booking.utils.constants.images import MAX_SIZE, ALLOWED_FORMATS


class PlacementImageSerializer(serializers.ModelSerializer):
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False),
        write_only=True,
        required=True
    )

    class Meta:
        model = PlacementImage
        fields = '__all__'
        read_only_fields = ['image', 'placement']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images')
        placement = self.context['placement']
        request = self.context['request']

        created_images = []

        for image in uploaded_images:
            image = PlacementImage.objects.create(placement=placement, image=image)
            created_images.append(request.build_absolute_uri(image.image.url))

        return created_images

    def validate_uploaded_images(self, uploaded_images):
        placement = self.context['placement']

        if uploaded_images is None:
            raise serializers.ValidationError({'uploaded_images': 'This field cannot be empty.'})

        if len(uploaded_images) > 15:
            raise serializers.ValidationError('The maximum number of images cannot exceed 15.')

        total_images = PlacementImage.objects.filter(placement=placement).count()

        allowed_number = 15 - total_images

        if allowed_number == 0:
            raise serializers.ValidationError('You have reached your image limit.')

        if len(uploaded_images) > allowed_number:
            raise serializers.ValidationError(f'You can add only {allowed_number} more image(s).')

        for image in uploaded_images:
            if image.size > MAX_SIZE:
                raise serializers.ValidationError('Each image must be smaller than 10 MB.')

            img = Image.open(image)

            if img.format not in ALLOWED_FORMATS:
                raise serializers.ValidationError(
                    {f'Image format must be one of the following: {', '.join(ALLOWED_FORMATS)}'})

        return uploaded_images

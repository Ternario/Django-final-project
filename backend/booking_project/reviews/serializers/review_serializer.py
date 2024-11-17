from rest_framework import serializers

from booking_project.booking_info.models.booking_details import BookingDetails
from booking_project.reviews.models.review import Review


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {'rating': {'required': True}}

    def validate(self, data):
        author = data.get('author')
        placement = data.get('placement')

        booking = BookingDetails.objects.filter(user=author, placement=placement)

        if not booking:
            raise serializers.ValidationError("You can't write review for apartments you didn't booked")

        if author == data.get('placement').owner:
            raise serializers.ValidationError("You can't write review for your own apartment")

        return data

    def create(self, validated_data):
        author = validated_data.pop('author')

        review = Review.objects.create(author=author, **validated_data)
        review.save()

        return review


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'author', 'placement', 'rating']
        extra_kwargs = {'feedback': {'required': True}}

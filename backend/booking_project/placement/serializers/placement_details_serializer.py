from django.db.models import Avg
from rest_framework import serializers

from booking_project.placement.models.placement_details import PlacementDetails
from booking_project.reviews.models.review import Review


class PlacementDetailSerializer(serializers.ModelSerializer):
    # rating = serializers.SerializerMethodField('avg_rating')
    #
    # def avg_rating(self, obj):
    #     count = Review.objects.filter(placement=obj.pk).aggregate(Avg('rating'))
    #     return count['rating__avg'] if count['rating__avg'] else 0

    class Meta:
        model = PlacementDetails
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'placement']

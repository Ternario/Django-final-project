from django.db import models
from rest_framework import serializers


class PlacementSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['title', 'category', 'location', 'rating', 'price', 'number_of_rooms',
                  'apartments_area']


class PlacementDetailSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']

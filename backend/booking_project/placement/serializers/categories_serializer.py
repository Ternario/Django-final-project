from rest_framework import serializers

from booking_project.placement.models.categories import Categories


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'

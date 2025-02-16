from rest_framework import serializers

from booking_project.models.category import Category


class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

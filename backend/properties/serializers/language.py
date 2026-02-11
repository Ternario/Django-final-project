from rest_framework.serializers import ModelSerializer

from properties.models import Language


class LanguageBaseSerializer(ModelSerializer):
    class Meta:
        model = Language
        fields = ['id', 'code']


class LanguageSerializer(ModelSerializer):
    class Meta:
        model = Language
        exclude = ['created_at', 'updated_at']

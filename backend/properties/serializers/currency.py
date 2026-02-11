from rest_framework.serializers import ModelSerializer

from properties.models import Currency


class CurrencyBaseSerializer(ModelSerializer):
    class Meta:
        model = Currency
        fields = ['id', 'code']


class CurrencySerializer(ModelSerializer):
    class Meta:
        model = Currency
        exclude = ['created_at', 'updated_at']

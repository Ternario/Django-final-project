from rest_framework.serializers import ModelSerializer

from properties.models import PaymentType


class PaymentTypeSerializer(ModelSerializer):
    class Meta:
        model = PaymentType
        exclude = ['created_at', 'updated_at']

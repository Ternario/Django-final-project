from rest_framework.serializers import ModelSerializer

from properties.models import PaymentMethod


class PaymentMethodSerializer(ModelSerializer):
    class Meta:
        model = PaymentMethod
        exclude = ['created_at', 'updated_at']

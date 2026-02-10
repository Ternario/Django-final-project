from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import AllowAny

from properties.models import PaymentMethod
from properties.serializers import PaymentMethodSerializer


class PaymentMethodLAV(ListAPIView):
    """
    View to retrieve a list of available payment methods.

    Returns all ayment methods records.

    Permissions:
        - AllowAny: accessible by any user, authorized or not.
    """
    permission_classes = [AllowAny]
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer


class PaymentMethodRAV(RetrieveAPIView):
    """
    View to retrieve detailed information about a single payment method by its ID.

    Permissions:
        - AllowAny: accessible by any user, authorized or not.
    """
    permission_classes = [AllowAny]
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer

    def get_object(self) -> PaymentMethod:
        return get_object_or_404(self.get_queryset(), id=self.kwargs['id'])

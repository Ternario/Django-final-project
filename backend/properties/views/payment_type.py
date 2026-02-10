from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import AllowAny

from properties.models import PaymentType
from properties.serializers import PaymentTypeSerializer


class PaymentTypeLAV(ListAPIView):
    """
    View to retrieve a list of available payment types.

    Returns all payment types records.

    Permissions:
        - AllowAny: accessible by any user, authorized or not.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    queryset = PaymentType.objects.all()
    serializer_class = PaymentTypeSerializer


class PaymentTypeRAV(RetrieveAPIView):
    """
    View to retrieve detailed information about a single payment type by its ID.

    Permissions:
        - AllowAny: accessible by any user, authorized or not.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    queryset = PaymentType.objects.all()
    serializer_class = PaymentTypeSerializer

    def get_object(self) -> PaymentType:
        return get_object_or_404(self.get_queryset(), id=self.kwargs['id'])

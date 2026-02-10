from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import AllowAny

from properties.models import Currency
from properties.serializers import CurrencySerializer, CurrencyBaseSerializer


class CurrencyLAV(ListAPIView):
    """
    View to retrieve a list of available currencies.

    Returns all currency records.

    Permissions:
        - AllowAny: accessible by any user, authorized or not.
    """
    permission_classes = [AllowAny]
    queryset = Currency.objects.all()
    serializer_class = CurrencyBaseSerializer


class CurrencyRAV(RetrieveAPIView):
    """
    View to retrieve detailed information about a single currency by its ID.

    Permissions:
        - AllowAny: accessible by any user, authorized or not.
    """
    permission_classes = [AllowAny]
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer

    def get_object(self) -> Currency:
        return get_object_or_404(self.get_queryset(), id=self.kwargs['id'])

from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import AllowAny

from properties.models import Language
from properties.serializers import LanguageSerializer


class LanguageLAV(ListAPIView):
    """
    View to retrieve a list of available languages.

    Returns all language records.

    Permissions:
        - AllowAny: accessible by any user, authorized or not.
    """
    permission_classes = [AllowAny]
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class LanguageRAV(RetrieveAPIView):
    """
    View to retrieve detailed information about a single language by its ID.

    Permissions:
        - AllowAny: accessible by any user, authorized or not.
    """
    permission_classes = [AllowAny]
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

    def get_object(self) -> Language:
        return get_object_or_404(self.get_queryset(), id=self.kwargs['id'])

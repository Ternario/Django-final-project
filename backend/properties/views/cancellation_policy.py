from rest_framework.generics import ListAPIView, RetrieveAPIView, get_object_or_404
from rest_framework.permissions import AllowAny

from properties.models import CancellationPolicy
from properties.serializers import CancellationPolicyBaseSerializer, CancellationPolicySerializer


class CancellationPolicyLAV(ListAPIView):
    """
    View to retrieve a list of available cancellation policies.

    Example of GET request:
    GET /cancellation-policies/

    Response:
    [
        {
            "id": 1,
            "name": "Flexible",
            "description": "Full refund 1 day prior to arrival."
        },
        ...
    ]

    Permissions:
        - AllowAny: accessible by any user, authorized or not.
    """
    permission_classes = [AllowAny]
    queryset = CancellationPolicy.objects.all()
    serializer_class = CancellationPolicyBaseSerializer


class CancellationPolicyRAV(RetrieveAPIView):
    """
    View to retrieve detailed information about a single cancellation policy.

    Example of GET request:
    GET /cancellation-policies/<id>/

    Response:
    {
        "id": 1,
        "name": "Flexible",
        "description": "Full refund 1 day prior to arrival."
    }

    Permissions:
        - AllowAny: accessible by any user, authorized or not.
    """
    permission_classes = [AllowAny]
    queryset = CancellationPolicy.objects.all()
    serializer_class = CancellationPolicySerializer

    def get_object(self) -> CancellationPolicy:
        return get_object_or_404(self.get_queryset(), id=self.kwargs['id'])

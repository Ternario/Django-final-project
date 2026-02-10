from typing import List, Dict, TYPE_CHECKING

from drf_spectacular.utils import extend_schema

from properties.utils.choices.booking import CancellationPolicy

if TYPE_CHECKING:
    from django.db.models import QuerySet

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from properties.models import AmenityCategory
from properties.serializers import AmenityCategorySerializer
from properties.utils.choices.property import PropertyType


class PropertyFiltersAV(APIView):
    """
    View to retrieve available property filters including amenities grouped by category,
    property types, and cancellation policies.

    Example of GET request:
    GET /properties/filters/

    Response:
    {
        'amenities_by_category': [
            {
                'id': 1,
                'name': 'Kitchen',
                'amenities': [
                    {'id': 3, 'name': 'Dishwasher'},
                    {'id': 4, 'name': 'Microwave'}
                ]
            },
            ...
        ],
        'property_types': [
            {'key': 'studio', 'label': 'Studio'},
            {'key': 'apartment', 'label': 'Apartment'}
        ],
        'property_policy': [
            {'key': 'flexible', 'label': 'Flexible'},
            {'key': 'moderate', 'label': 'Moderate'}
        ]
    }

    Permissions:
        - AllowAny: accessible by any user, authorized or not.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=None,
        responses={200: None},
        description='Return dict of filters'
    )
    def get(self, request, *args, **kwargs) -> Response:
        queryset: QuerySet[AmenityCategory] = AmenityCategory.objects.all().order_by('name').prefetch_related(
            'amenities')

        property_types: List[Dict[str, str]] = [{'key': key, 'label': label} for key, label in PropertyType.choices()]
        property_policy: List[Dict[str, str]] = [{'key': key, 'label': label} for key, label in
                                                 CancellationPolicy.choices()]

        return Response({
            'amenities_by_category': AmenityCategorySerializer(queryset, many=True).data,
            'property_types': property_types,
            'property_policy': property_policy
        },
            status=status.HTTP_200_OK
        )

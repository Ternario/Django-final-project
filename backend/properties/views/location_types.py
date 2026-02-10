from typing import List

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import BasePermission, SAFE_METHODS, AllowAny
from rest_framework.viewsets import ModelViewSet

from properties.models import Country, Region, City
from properties.permissions import StaffOnly
from properties.serializers import CountrySerializer, RegionSerializer, CitySerializer


class CountryMVS(ModelViewSet):
    """
    ViewSet for managing Country resources.

    Provides list, retrieve, create, update, and delete actions.
    """
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]

        return [StaffOnly()]


class RegionMVS(ModelViewSet):
    """
    ViewSet for managing Region resources.

    Provides list, retrieve, create, update, and delete actions.
    Supports filtering by country ID using query parameter `?country=<id>`.
    """
    serializer_class = RegionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country']

    def get_queryset(self) -> QuerySet[Region]:
        return Region.objects.all().select_related('country')

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]

        return [StaffOnly()]


class CityMVS(ModelViewSet):
    """
    ViewSet for managing City resources.

    Provides list, retrieve, create, update, and delete actions.
    Supports filtering by country ID and region ID using query parameters:
        - `?country=<id>`
        - `?region=<id>`
    """
    serializer_class = CitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['country', 'region']

    def get_queryset(self) -> QuerySet[City]:
        return City.objects.all().select_related('country', 'region')

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]

        return [StaffOnly()]

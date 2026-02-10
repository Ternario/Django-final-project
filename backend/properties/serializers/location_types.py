from rest_framework.serializers import ModelSerializer, CharField

from properties.models import Country, Region, City


class CountrySerializer(ModelSerializer):
    class Meta:
        model = Country
        exclude = ['created_at', 'updated_at']


class RegionSerializer(ModelSerializer):
    country_name = CharField(source='country.name', read_only=True)

    class Meta:
        model = Region
        exclude = ['created_at', 'updated_at']


class CitySerializer(ModelSerializer):
    region_name = CharField(source='region.name', read_only=True)
    country_name = CharField(source='country.name', read_only=True)

    class Meta:
        model = City
        exclude = ['created_at', 'updated_at']

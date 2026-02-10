from django_filters import FilterSet, CharFilter, NumberFilter, ModelMultipleChoiceFilter
from django.db.models import Q, F, ExpressionWrapper
from rest_framework.fields import DecimalField

from properties.models import Property, Booking, Language, CompanyMembership, Amenity


class PropertyFilter(FilterSet):
    city = CharFilter(method='filter_city')
    price_gte = NumberFilter(field_name='price')
    price_lte = NumberFilter(field_name='price')
    rating_gte = NumberFilter(field_name='rating', lookup_expr='gte')
    property_type = CharFilter(field_name='property_type', lookup_expr='iexact')

    amenities = ModelMultipleChoiceFilter(
        field_name='amenities',
        queryset=Amenity.objects.all(),
        to_field_name='name',
        conjoined=True
    )

    def filter_city(self, queryset, name, value):
        return queryset.filter(property_ref__location__city=value)

    def filter_price_gte(self, queryset, name, value):
        total_price = ExpressionWrapper(F('base_price') + F('taxes_fees'), output_field=DecimalField(
            max_digits=10, decimal_places=2
        ))
        return queryset.annotate(total_price=total_price).filter(total_price__gte=value)

    def filter_price_lte(self, queryset, name, value):
        total_price = ExpressionWrapper(F('base_price') + F('taxes_fees'), output_field=DecimalField(
            max_digits=10, decimal_places=2
        ))
        return queryset.annotate(total_price=total_price).filter(total_price__lte=value)

    class Meta:
        model = Property
        fields = ['city', 'price_gte', 'price_lte', 'rating_gte', 'property_type']


class BookingFilter(FilterSet):
    property = NumberFilter(field_name='property_ref_id')
    status = CharFilter(field_name='status', lookup_expr='iexact')

    class Meta:
        model = Booking
        fields = ['property', 'status']


class CompanyMembershipFilter(FilterSet):
    language = ModelMultipleChoiceFilter(
        field_name='languages_spoken',
        queryset=Language.objects.all(),
        conjoined=True
    )

    class Meta:
        model = CompanyMembership
        fields = ['role', 'language', 'joined_at', 'is_active', 'left_at']

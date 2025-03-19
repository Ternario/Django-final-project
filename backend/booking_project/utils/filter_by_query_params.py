import django_filters
from django.db.models import Q

from booking_project.models import Placement


class PlacementFilter(django_filters.FilterSet):
    text = django_filters.CharFilter(method='filter_text')
    description = django_filters.CharFilter(method='filter_description')
    city = django_filters.CharFilter(method='filter_city')
    category = django_filters.CharFilter(method='filter_category')
    price_gte = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_lte = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    rating_gte = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    no_rooms = django_filters.CharFilter(method='filter_no_rooms')
    details = django_filters.CharFilter(method='filter_details')

    def filter_text(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))

    def filter_description(self, queryset, name, value):
        return queryset.filter(description__icontains=value)

    def filter_city(self, queryset, name, value):
        return queryset.filter(placement_location__city__in=value.split(","))

    def filter_category(self, queryset, name, value):
        return queryset.filter(category__name__in=value.split(","))

    def filter_no_rooms(self, queryset, name, value):
        room_list = value.split(",")
        return queryset.filter(number_of_rooms__in=room_list)

    def filter_details(self, queryset, name, value):
        q_objects = Q()
        for detail in value.split(","):
            q_objects &= Q(**{f'placement_details__{detail}': True})
        return queryset.filter(q_objects)

    class Meta:
        model = Placement
        fields = []

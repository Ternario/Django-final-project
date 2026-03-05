from django_filters import FilterSet, CharFilter, NumberFilter, ModelMultipleChoiceFilter, DateFilter

from properties.models import Property, Booking, Language, CompanyMembership, Amenity


class PropertyFilter(FilterSet):
    city = CharFilter(field_name='location__city')
    property_type = CharFilter(field_name='property_type', lookup_expr='iexact')
    price_gte = NumberFilter(field_name='discounted_price', lookup_expr='gte')
    price_lte = NumberFilter(field_name='discounted_price', lookup_expr='lte')
    guests_number = CharFilter(field_name='max_guests')
    no_rooms = CharFilter(field_name='detail__number_of_rooms')
    rating_gte = NumberFilter(field_name='rating', lookup_expr='gte')

    check_in = DateFilter(method='filter_availability', label='Check In')
    check_out = DateFilter(method='filter_availability', label='Check Out')

    amenities = ModelMultipleChoiceFilter(
        field_name='amenities',
        queryset=Amenity.objects.all(),
        to_field_name='name',
        conjoined=True
    )

    class Meta:
        model = Property
        fields = ['city', 'property_type', 'price_gte', 'price_lte', 'guests_number', 'no_rooms', 'rating_gte',
                  'check_in', 'check_out', 'amenities']

    def filter_availability(self, queryset, name, value):
        check_in: str = self.data.get('check_in')
        check_out: str = self.data.get('check_out')

        if not check_in or not check_out:
            return queryset

        return queryset.exclude(
            bookings__check_in__lt=check_out,
            bookings__check_out__gt=check_in
        )


class BookingFilter(FilterSet):
    property = NumberFilter(field_name='property_ref_id')
    status = CharFilter(field_name='status', lookup_expr='iexact')
    city = CharFilter(field_name='property_ref__location__city', lookup_expr='iexact')

    class Meta:
        model = Booking
        fields = ['property', 'status', 'city']


class CompanyMembershipFilter(FilterSet):
    language = ModelMultipleChoiceFilter(
        field_name='languages_spoken',
        queryset=Language.objects.all(),
        conjoined=True
    )

    class Meta:
        model = CompanyMembership
        fields = ['role', 'language', 'joined_at', 'is_active', 'left_at']

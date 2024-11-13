from datetime import datetime

from django.db.models import Q
from rest_framework import serializers

from booking_project.booking_info.models.booking_details import BookingDetails
from booking_project.placement.serializers.placement_serializer import PlacementSerializer
from booking_project.users.serialezers.user_serializer import UserBaseDetailSerializer


class BookingDatesCreateSerializer(serializers.ModelSerializer):
    user = UserBaseDetailSerializer(read_only=True)

    class Meta:
        model = BookingDetails
        fields = '__all__'
        read_only_fields = ['is_active', 'is_confirmed', 'is_cancelled']

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date < datetime.today().date():
            raise serializers.ValidationError("Start date can't be in the past")
        if end_date <= start_date:
            raise serializers.ValidationError("The end date must be at least one day later than the start date ")

        # user = data.get('user')
        #
        # if user == data.get('placement').owner:
        #     raise serializers.ValidationError("You can't booking your own apartment")

        overlapping_reservations = BookingDetails.objects.filter(
            placement=data.get('placement')
        ).filter(
            Q(start_date__lt=end_date) &
            Q(end_date__gt=start_date) &
            Q(is_active=True) &
            Q(is_cancelled=False)
        )

        if overlapping_reservations.exists():
            raise serializers.ValidationError('This apartment is already reserved for the selected dates.')

        return data


class BookingDatesUserSerializer(serializers.ModelSerializer):
    placement = PlacementSerializer(read_only=True)

    class Meta:
        model = BookingDetails
        fields = ['start_date', 'end_date', 'is_confirmed', 'is_cancelled', 'is_active',
                  'created_at']
        only_read_fields = ['placement__title', 'is_confirmed', 'created_at']


class BookingDatesOwnerSerializer(serializers.ModelSerializer):
    user = UserBaseDetailSerializer(read_only=True)

    class Meta:
        model = BookingDetails
        fields = ['placement__title', '' 'start_date', 'end_date', 'is_confirmed', 'is_cancelled', 'is_active',
                  'created_at']
        only_read_fields = ['created_at', 'user__first_name', 'user__last_name']

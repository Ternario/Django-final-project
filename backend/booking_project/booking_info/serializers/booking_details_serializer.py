from datetime import datetime

from django.db.models import Q
from rest_framework import serializers

from booking_project.booking_info.models.booking_details import BookingDetails


class BookingDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDetails
        fields = '__all__'
        read_only_fields = ['is_active', 'is_confirmed', 'is_cancelled']

    def validate(self, data):
        placement = data.get('placement')
        user = data.get('user')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        print(data)
        if start_date < datetime.today().date():
            raise serializers.ValidationError("Start date can't be in the past")
        if end_date <= start_date:
            raise serializers.ValidationError("The end date must be at least one day later than the start date ")

        if user == data.get('placement').owner:
            raise serializers.ValidationError("You can't booking your own apartment")

        bookings = BookingDetails.objects.filter(
            placement=placement
        ).filter(
            Q(start_date__lt=end_date) &
            Q(end_date__gt=start_date) &
            Q(is_active=True) &
            Q(is_cancelled=False)
        )

        if bookings.exists():
            raise serializers.ValidationError('This apartment is already reserved for the selected dates.')

        return data

    def create(self, validated_data):
        user = validated_data.pop('user')

        booking = BookingDetails.objects.create(user=user, **validated_data)
        booking.save()

        return booking


class BookingDetailsUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDetails
        fields = ['start_date', 'end_date', 'is_confirmed', 'is_cancelled', 'is_active',
                  'created_at']
        read_only_fields = ['is_confirmed', 'created_at', 'updated_at', 'start_date', 'end_date', 'is_active']


class BookingDetailsOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingDetails
        fields = ['is_confirmed', 'is_cancelled', 'placement', 'user', 'created_at', 'updated_at', 'start_date',
                  'end_date', 'is_active']
        read_only_fields = ['created_at', 'updated_at', 'start_date', 'end_date']

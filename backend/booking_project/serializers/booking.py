from datetime import timedelta

from django.db.models import Q
from django.utils.timezone import now
from rest_framework import serializers

from booking_project.models.booking import Booking
from booking_project.models.choices import BookingStatus
from booking_project.serializers.user import UserBaseDetailSerializer


def validate_cancel(instance, user, reason):
    if instance.status == BookingStatus.CANCELLED.value:
        raise serializers.ValidationError('This booking is already cancelled.')

    cancel_date = instance.check_in_date - timedelta(days=2)

    if now().date() >= cancel_date:
        raise serializers.ValidationError('You cannot cancel the booking less than two days in advance.')

    if not reason or len(reason) < 40:
        raise serializers.ValidationError({
            'cancellation_reason': 'This field is required when booking is being cancelled and must be at least 40 characters long.'
        })

    instance.status = BookingStatus.CANCELLED.value
    instance.is_active = False
    instance.cancelled_by = user
    instance.cancellation_reason = reason
    instance.cancelled_at = now()
    instance.save()

    return instance


class BookingCreateSerializer(serializers.ModelSerializer):
    placement_name = serializers.CharField(source='placement.title', read_only=True)
    check_in_time = serializers.TimeField(format='%H:%M')
    check_out_time = serializers.TimeField(format='%H:%M')

    class Meta:
        model = Booking
        exclude = ['status', 'cancelled_by', 'cancellation_reason', 'cancelled_at', 'created_at', 'updated_at',
                   'is_active']
        read_only_fields = ['user', 'placement_name']

    def create(self, validated_data):

        booking = Booking.objects.create(**validated_data)

        return booking

    def validate(self, data):
        user = self.context['user']
        placement = data.get('placement')
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')

        if user == data.get('placement').owner:
            raise serializers.ValidationError({'user': 'You can\'t booking your own apartment.'})

        if check_in_date < now().date():
            raise serializers.ValidationError({'check_in_date': 'Start date can\'t be in the past.'})

        if check_out_date <= check_in_date:
            raise serializers.ValidationError(
                {'check_out_date': 'The end date must be at least one day later than the start date.'}
            )

        bookings = Booking.objects.filter(
            placement=placement,
        ).filter(Q(check_in_date__lt=check_out_date) & Q(check_out_date__gt=check_in_date))

        if bookings.exists():
            raise serializers.ValidationError('This apartment is already reserved for the selected dates.')

        data['user'] = user

        return data


class BookingBaseDetailsSerializer(serializers.ModelSerializer):
    placement_name = serializers.CharField(source='placement.title', read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'placement', 'placement_name', 'check_in_date', 'check_out_date', 'status']


class BookingDetailsPlacementOwnerSerializer(serializers.ModelSerializer):
    user = UserBaseDetailSerializer(read_only=True)
    placement_name = serializers.CharField(source='placement.title', read_only=True)
    check_in_time = serializers.TimeField(format='%H:%M', read_only=True)
    check_out_time = serializers.TimeField(format='%H:%M', read_only=True)
    cancelled_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)
    cancelled_by_role = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Booking
        exclude = ['is_active']
        read_only_fields = ['placement', 'user', 'check_in_date', 'check_out_date', 'status', 'cancelled_by',
                            'cancelled_at', 'created_at', 'updated_at']

    def get_cancelled_by_role(self, obj):
        if obj.cancelled_by == obj.placement.owner:
            return 'Owner'
        elif obj.cancelled_by == obj.user:
            return 'User'
        else:
            return

    def validate(self, data):
        reason = data.get('cancellation_reason')
        instance = self.instance
        cancelled_by = instance.placement.owner
        validate_cancel(instance, cancelled_by, reason)
        return data


class BookingDetailsOwnerSerializer(serializers.ModelSerializer):
    placement_name = serializers.CharField(source='placement.title', read_only=True)
    check_in_time = serializers.TimeField(format='%H:%M', read_only=True)
    check_out_time = serializers.TimeField(format='%H:%M', read_only=True)
    cancelled_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M", read_only=True)
    cancelled_by_role = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Booking
        exclude = ['is_active']
        read_only_fields = ['placement', 'user', 'check_in_date', 'check_out_date', 'status', 'cancelled_by',
                            'cancelled_at', 'created_at', 'updated_at']

    def get_cancelled_by_role(self, obj):
        if obj.cancelled_by == obj.placement.owner:
            return 'Owner'
        elif obj.cancelled_by == obj.user:
            return 'User'
        else:
            return

    def validate(self, data):
        reason = data.get('cancellation_reason')
        instance = self.instance
        cancelled_by = instance.user
        validate_cancel(instance, cancelled_by, reason)
        return data

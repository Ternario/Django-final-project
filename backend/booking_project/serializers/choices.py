from rest_framework import serializers

from booking_project.models.choices import CheckInTime, CheckOutTime


class BookingTimeChoicesSerializer(serializers.Serializer):
    check_in_time = serializers.SerializerMethodField()
    check_out_time = serializers.SerializerMethodField()

    def get_check_in_time(self, obj):
        return CheckInTime.choices()

    def get_check_out_time(self, obj):
        return CheckOutTime.choices()

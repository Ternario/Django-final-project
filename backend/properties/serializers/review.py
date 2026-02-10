from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Any, List

if TYPE_CHECKING:
    from properties.models import User
from datetime import datetime, date

from django.utils import timezone
from rest_framework.serializers import ModelSerializer, ValidationError, CharField, SerializerMethodField

from properties.models import Review, Booking
from properties.serializers.user import UserBasePublicSerializer
from properties.utils.error_messages.review import REVIEW_ERRORS


class ReviewCreateSerializer(ModelSerializer):
    status_display = CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Review
        exclude = ['author_token']
        read_only_fields = ['id', 'author_username', 'property_ref', 'status', 'owner_response', 'moderator_notes',
                            'rejected_reason', 'is_deleted', 'deleted_at', 'created_at', 'updated_at']

    def create(self, validated_data: Dict[str, Any]) -> Review:
        author: User = self.context['user']
        booking: Booking = self.context['booking']

        validated_data['author'] = author
        validated_data['booking'] = booking
        validated_data['property_ref'] = booking.property_ref

        return super().create(validated_data)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        author: User = self.context['user']
        booking: Booking = self.context['booking']
        rating: int = attrs.get('rating')
        feedback: str | None = attrs.get('feedback', None)

        non_field_errors: List[str] = []

        if rating < 5 and not feedback:
            non_field_errors.append(REVIEW_ERRORS['feedback_required'])

        if not Booking.objects.inactive(guest_id=author.pk, property_ref_id=booking.property_ref_id).exists():
            non_field_errors.append(REVIEW_ERRORS['no_booking'])

        if booking.is_active:
            non_field_errors.append(REVIEW_ERRORS['active_booking'])

        check_cancelled_datetime: datetime = timezone.make_aware(
            timezone.datetime.combine(booking.check_in_date, booking.check_in_time))

        if booking.cancelled_at < check_cancelled_datetime:
            non_field_errors.append(REVIEW_ERRORS['cancelled_before_start'])

        if Review.objects.published(author_id=author.pk, booking_id=booking.pk).exists():
            non_field_errors.append(REVIEW_ERRORS['duplicate'])

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

        return attrs


class ReviewListSerializer(ModelSerializer):
    owner_response_by = UserBasePublicSerializer(read_only=True)
    moderator_notes_by = UserBasePublicSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'author', 'author_username', 'rating', 'feedback', 'owner_response', 'owner_response_by',
                  'moderator_notes', 'moderator_notes_by', 'created_at', 'updated_at']


class ReviewAuthorListSerializer(ModelSerializer):
    status = CharField(source='get_status_display', read_only=True)
    booking_date = SerializerMethodField('get_booking_date', read_only=True)
    property_name = CharField(source='property_ref.title', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'booking_date', 'author', 'property_ref', 'property_name', 'rating', 'feedback', 'status']

    def get_booking_date(self) -> str:
        booking: Booking = self.instance.booking
        check_in: date = booking.check_in_date
        check_out: date = booking.check_out_date

        if check_in.year == check_out.year and check_in.month == check_out.month:
            month: str = check_in.strftime('%b')
            return f'{check_in.day} - {check_out.day} {month} {check_in.year}'

        if check_in.year == check_out.year:
            return f'{check_in.day}.{check_in.month} - {check_out.day}.{check_out.month} {check_out.year}'

        check_in_formatted: str = check_in.strftime('%d.%m.%Y')
        check_out_formatted: str = check_out.strftime('%d.%m.%Y')

        return f'{check_in_formatted} - {check_out_formatted}'


class ReviewAuthorSerializer(ModelSerializer):
    status = CharField(source='get_status_display', read_only=True)
    owner_response_by = UserBasePublicSerializer(read_only=True)
    moderator_notes_by = UserBasePublicSerializer(read_only=True)

    class Meta:
        model = Review
        exclude = ['author_token']
        read_only_fields = ['id', 'booking', 'author', 'author_username', 'property_ref', 'status', 'owner_response',
                            'moderator_notes', 'rejected_reason', 'is_deleted', 'deleted_at', 'created_at',
                            'updated_at']

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        rating: int = attrs.get('rating') or self.instance.rating
        feedback: str | None = attrs.get('feedback', None)

        non_field_errors: List[str] = []

        if rating < 1 or rating > 5:
            non_field_errors.append(REVIEW_ERRORS['false_rating'])

        if rating < 5 and not feedback:
            non_field_errors.append(REVIEW_ERRORS['feedback_required'])

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

        return attrs


class ReviewPropertyOwnerSerializer(ModelSerializer):
    status = CharField(source='get_status_display', read_only=True)
    owner_response_by = UserBasePublicSerializer(read_only=True)
    moderator_notes_by = UserBasePublicSerializer(read_only=True)

    class Meta:
        model = Review
        exclude = ['author_token']
        read_only_fields = ['id', 'booking', 'author', 'author_username', 'property_ref', 'rating',
                            'feedback', 'moderator_notes', 'rejected_reason', 'is_deleted', 'deleted_at', 'created_at',
                            'updated_at']

    def update(self, instance: Review, validated_data: Dict[str, Any]) -> Review:
        owner_response_by: User = self.context['user']

        validated_data['owner_response_by'] = owner_response_by

        return super().update(instance, validated_data)

    def validate_owner_response(self, owner_response: str) -> str:
        if not owner_response or (len(owner_response.strip()) < 10 or len(owner_response.strip()) > 2000):
            raise ValidationError({'owner_response': REVIEW_ERRORS['owner_response']})

        return owner_response

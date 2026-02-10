from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from properties.models import User
    from datetime import datetime

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator, MaxValueValidator, MinValueValidator
from django.utils import timezone
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from properties.managers.review import CustomReviewManager
from properties.models import Booking
from properties.utils.choices.review import ReviewStatus
from properties.utils.constants.default_depersonalization_values import DELETED_USER_PLACEHOLDER
from properties.utils.error_messages.review import REVIEW_ERRORS
from properties.utils.user_token_generation import make_user_token
from properties.utils.error_messages.not_null_field import NOT_NULL_FIELD


class Review(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.SET_NULL, null=True, related_name='reviews',
                                verbose_name=_('Booking'))
    author = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='reviews',
                               verbose_name=_('Author'))
    author_token = models.CharField(max_length=64, blank=True, null=True, db_index=True, verbose_name=_('Author token'))
    author_username = models.CharField(max_length=155, blank=True, verbose_name=_('Author username'))
    property_ref = models.ForeignKey('Property', on_delete=models.SET_NULL, blank=True, null=True, db_index=True,
                                     related_name='reviews', verbose_name=_('Property'))
    status = models.CharField(max_length=20, choices=ReviewStatus.choices(), default=ReviewStatus.PUBLISHED.value[0],
                              verbose_name=_('Status'))
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)],
                                              verbose_name=_('Rating'))
    feedback = models.TextField(blank=True, validators=[MinLengthValidator(10), MaxLengthValidator(2000)],
                                verbose_name=_('Feedback'))
    owner_response = models.TextField(validators=[MinLengthValidator(10), MaxLengthValidator(2000)], blank=True,
                                      verbose_name=_('Owner response'))
    owner_response_by = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True,
                                          related_name='review_property_owners', verbose_name=_('Owner response by'))

    moderator_notes = models.TextField(validators=[MinLengthValidator(10), MaxLengthValidator(2000)], blank=True,
                                       verbose_name=_('Moderator notes'))
    moderator_notes_by = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True,
                                           related_name='review_moderators', verbose_name=_('Moderator notes by'))

    rejected_reason = models.TextField(validators=[MinLengthValidator(10), MaxLengthValidator(2000)], blank=True,
                                       verbose_name=_('Rejected reason'))
    is_deleted = models.BooleanField(default=False, verbose_name=_('Deleted'))
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name=_('Deleted at'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = CustomReviewManager()

    def __str__(self) -> str:
        return f'Review by {self.author} to {self.property_ref}, ({self.rating}/5).'

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')

    @property
    def check_cancelled_datetime(self) -> datetime:
        return timezone.make_aware(timezone.datetime.combine(self.booking.check_in_date, self.booking.check_in_time))

    def clean(self) -> None:
        super().clean()

        errors: Dict[str, str] = {}

        if not self.booking_id:
            errors['booking'] = NOT_NULL_FIELD

        if not self.author_id:
            errors['author'] = NOT_NULL_FIELD

        if errors:
            raise ValidationError(errors)

        non_field_errors: List[str] = []

        if self.rating < 5 and not self.feedback:
            non_field_errors.append(REVIEW_ERRORS['feedback_required'])

        if not Booking.objects.inactive(guest=self.author, property_ref=self.property_ref).exists():
            non_field_errors.append(REVIEW_ERRORS['no_booking'])

        if self.booking.is_active:
            non_field_errors.append(REVIEW_ERRORS['active_booking'])

        if self.booking.cancelled_at is not None and self.booking.cancelled_at < self.check_cancelled_datetime:
            non_field_errors.append(REVIEW_ERRORS['cancelled_before_start'])

        if Review.objects.published(author=self.author, booking=self.booking).exclude(id=self.pk).exists():
            non_field_errors.append(REVIEW_ERRORS['duplicate'])

        if self.status == ReviewStatus.REJECTED.value[0] and not self.rejected_reason:
            raise ValidationError({'non_field_errors': [REVIEW_ERRORS['rejected_reason']]})

        if non_field_errors:
            raise ValidationError({'non_field_errors': non_field_errors})

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()

        if not self.property_ref:
            self.property_ref = self.booking.property_ref_id

        if not self.author_username:
            author: User = self.author
            if author.username:
                self.author_username = author.username
            else:
                self.author_username = author.first_name
        super().save(*args, **kwargs)

    def soft_delete(self, feedback: str | None = None) -> None:
        if self.is_deleted:
            return
        self.author_username = DELETED_USER_PLACEHOLDER
        self.status = ReviewStatus.DELETED.value[0]
        self.feedback = feedback if feedback else ''
        self.is_deleted = True
        self.deleted_at = now()
        self.save(update_fields=['author_username', 'status', 'feedback', 'is_deleted', 'deleted_at'])

    def privacy_delete(self, feedback: str | None = None) -> None:
        if not self.author:
            return
        self.author_username = DELETED_USER_PLACEHOLDER
        self.author_token = make_user_token(self.author.pk)
        self.author = None
        self.status = ReviewStatus.PRIVACY_REMOVED.value[0]
        self.feedback = feedback if feedback else ''
        self.is_deleted = True
        self.save(
            update_fields=['author_username', 'author_token', 'author', 'feedback', 'status', 'is_deleted']
        )

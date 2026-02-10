from typing import Any
from decimal import Decimal

from django.db import models

from django.core.validators import MinLengthValidator, MinValueValidator, MaxLengthValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from properties.managers.property import CustomPropertyManager
from properties.models.property_slug_history import PropertySlugHistory

from properties.utils.choices.property import PropertyType, PropertyAvailabilityStatus, PropertyApprovalStatus


class Property(models.Model):
    owner = models.ForeignKey('LandlordProfile', on_delete=models.PROTECT, related_name='properties',
                              verbose_name=_('Owner'))
    created_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_properties',
                                   verbose_name=_('created_by'))
    title = models.CharField(max_length=255, unique=True, verbose_name=_('Property title'))
    slug = models.SlugField(max_length=255, blank=True, unique=True, db_index=True, verbose_name=_('Slug'))
    description = models.TextField(validators=[MinLengthValidator(40), MaxLengthValidator(2000)], blank=False,
                                   verbose_name=_('Property description'))
    property_type = models.CharField(max_length=15, db_index=True, choices=PropertyType.choices(),
                                     default=PropertyType.APARTMENT.value[0], verbose_name=_('Property type'))
    amenities = models.ManyToManyField('Amenity', related_name='properties', verbose_name=_('amenities'))
    base_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('10.00'))],
                                     verbose_name=_('Base price'))
    taxes_fees = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))],
                                     default=Decimal('0.00'), verbose_name=_('Taxes fees'))
    payment_types = models.ManyToManyField('PaymentType', related_name='properties', verbose_name=_('Payment type'))
    min_stay = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name=_('Min stay'))
    max_guests = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name=_('Max guests'))
    rating = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(5)],
                                              verbose_name=_('Rating'))
    review_count = models.PositiveIntegerField(default=0, validators=[MinValueValidator(8)],
                                               verbose_name=_('Review count'))
    cancellation_policy = models.ForeignKey('CancellationPolicy', on_delete=models.PROTECT, related_name='properties',
                                            verbose_name=_('Cancellation policy'))
    house_rules = models.TextField(blank=True, validators=[MaxLengthValidator(2000)], verbose_name=_('House rules'))
    status = models.CharField(max_length=20, db_index=True, choices=PropertyAvailabilityStatus.choices(),
                              default=PropertyAvailabilityStatus.INACTIVE.value[0], verbose_name=_('Status'))
    approval_status = models.CharField(max_length=20, choices=PropertyApprovalStatus.choices(),
                                       default=PropertyApprovalStatus.PENDING.value[0],
                                       verbose_name=_('Approval status'))
    auto_confirm_bookings = models.BooleanField(default=False, verbose_name=_('Auto confirmation bookings'))

    is_deleted = models.BooleanField(default=False, verbose_name=_('Deleted'))
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Deleted at'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = CustomPropertyManager()

    def __str__(self) -> str:
        return f'Property: {self.title}, type: {self.property_type} by landlord: {self.owner}.'

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Property')
        verbose_name_plural = _('Properties')

    def save(self, *args: Any, **kwargs: Any) -> None:
        self.full_clean()

        if not self.slug or self._check_title_is_changed():
            old_slug: str = self.slug
            base_slug: str = slugify(self.title)
            slug: str = base_slug
            counter: int = 1

            while Property.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1

            if old_slug:
                PropertySlugHistory.objects.get_or_create(property_ref=self, old_slug=old_slug)

            self.slug = slug

        if self.approval_status == PropertyApprovalStatus.PENDING.value[0] and self.owner.is_trusted:
            self.approval_status = PropertyApprovalStatus.AUTO_APPROVED.value[0]

        super().save(*args, **kwargs)

    def _check_title_is_changed(self) -> bool:
        if not self.pk:
            return False

        old_title: Property = Property.objects.filter(pk=self.pk).only('title').first()

        return old_title and old_title.title != self.title

    def soft_delete(self) -> None:
        if self.is_deleted:
            return

        self.status = PropertyAvailabilityStatus.DELETED.value[0]
        self.is_deleted = True

        if not self.deleted_at:
            self.deleted_at = now()
        self.save(update_fields=['status', 'is_deleted', 'deleted_at', 'updated_at'])

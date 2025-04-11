from django.db import models


class BookingManager(models.Manager):
    def create(self, **kwargs):
        instance = self.model(**kwargs)
        instance.full_clean()
        instance.save()
        return instance


class FilterActiveBookingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class FilterNotActiveBookingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=False)

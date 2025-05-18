from django.db import models


class FilterActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, is_active=True)


class FilterNotActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, is_active=False)


class FilterDeletedManagers(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=True)


class FilterNotDeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class FilterPlacementRelatedManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(placement__is_deleted=False)

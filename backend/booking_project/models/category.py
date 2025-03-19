from django.db import models


class Category(models.Model):
    objects = models.Manager()

    name = models.CharField(max_length=100, unique=True, verbose_name='Category')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'categories'

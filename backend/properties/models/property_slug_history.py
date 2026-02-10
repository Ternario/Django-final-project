from django.db import models
from django.utils.text import gettext_lazy as _


class PropertySlugHistory(models.Model):
    property_ref = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='slug_history',
                                     verbose_name=_('Property'))
    old_slug = models.SlugField(max_length=255, unique=True, verbose_name=_('Old slug'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Property slug history')
        verbose_name_plural = _('Property slug histories')

    def __str__(self) -> str:
        return f'Property slug {self.old_slug} for property {self.property_ref}'

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MinLengthValidator, MaxLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from properties.managers.deletion_log import DeletionLogManager
from properties.utils.choices.deletion import DeletionType


class DeletionLog(models.Model):
    """
    Logs deletions or privacy removals of various models for auditing purposes.

    Fields:
    - deleted_by: User who performed deletion.
    - deleted_model: ContentType of the deleted model.
    - deleted_model_name: App label and name of the deleted model.
    - deleted_object_id: ID of the deleted object.
    - deleted_object: GenericForeignKey pointing to the deleted object (if still accessible).
    - reason: Reason for delete (e.g., 'Cascade', user request, admin action).
    - deleted_at: Timestamp when delete occurred.
    - parent_log: Optional link to a parent log entry (for cascade deletions).
    - parent_log_name: Name of the parent log entry (for convenience).
    """
    deleted_by = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='deletions',
                                   verbose_name=_('Deleted by'))
    deleted_by_token = models.CharField(max_length=64, blank=True, null=True, db_index=True,
                                        verbose_name=_('Deleted by token'))
    deleted_model = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True,
                                      verbose_name=_('Deleted model'))
    deleted_model_name = models.CharField(max_length=100, verbose_name=_('Deleted model name'))
    deleted_object_id = models.PositiveIntegerField(validators=[MinValueValidator(1)],
                                                    verbose_name=_('Deleted model id'))
    deleted_object = GenericForeignKey('deleted_model', 'deleted_object_id')
    reason = models.TextField(validators=[MinLengthValidator(7), MaxLengthValidator(2000)], blank=True, null=True,
                              verbose_name=_('Reason'))
    deletion_type = models.CharField(max_length=20, choices=DeletionType.choices(),
                                     default=DeletionType.SOFT_DELETE.value, verbose_name=_('Deletion type'))
    is_cascade = models.BooleanField(default=False, verbose_name=_('Cascade delete'))
    parent_log = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name=_('Parent log'))
    parent_log_name = models.CharField(max_length=155, verbose_name=_('Parent log name'))
    deleted_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Deleted at'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated at'))

    objects = DeletionLogManager()

    def __str__(self):
        return (
            f'Model: {self.deleted_model_name}, id: {self.deleted_object_id}, '
            f'deleted by: {self.deleted_by if self.deleted_by else self.deleted_by_token}.'
        )

from enum import Enum

from properties.utils.choices.enumMixin import ChoicesEnumMixin


class DeletionType(ChoicesEnumMixin, Enum):
    """
    Methods for deleting a model instance in the system.

    - CASCADE: The object is deleted along with all related objects.
    - SOFT_DELETE: The object is marked as deleted without removing it from the database.
    - PRIVACY_DELETE: The object is anonymized or removed for privacy reasons, preserving system integrity.
    """
    CASCADE = ('CASCADE', 'Cascade')
    SOFT_DELETE = ('SOFT_DELETE', 'Soft delete')
    PRIVACY_DELETE = ('PRIVACY_DELETE', 'Privacy delete')

from enum import Enum

from properties.utils.choices.enumMixin import ChoicesEnumMixin


class UserDeleteStatus(ChoicesEnumMixin, Enum):
    """
    Represents the deletion types of a user within the system.

    - SOFT: The user account is soft-deleted and can potentially be restored.
    - PRIVACY: The user account is deleted for privacy reasons
    and associated personal data may be removed or anonymized.
    - NONE: The user is active.
    """
    SOFT = ('SOFT', 'Soft')
    PRIVACY = ('PRIVACY', 'Privacy')
    NONE = ('NONE', 'None')

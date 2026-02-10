from enum import Enum

from properties.utils.choices.enumMixin import ChoicesEnumMixin


class DetailsAccess(ChoicesEnumMixin, Enum):
    """
    Types of bathroom access for a property.

    - PRIVATE: Bathroom is private to the guest.
    - SHARED: Bathroom is shared with other guests or residents.
    - NONE: Bathroom access is not specified.
    """
    PRIVATE = ('PRIVATE', 'private')
    SHARED = ('SHARED', 'Shared')
    NONE = ('NONE', 'Not specified')
from enum import Enum

from properties.utils.choices.enumMixin import ChoicesEnumMixin


class ProfileTheme(ChoicesEnumMixin, Enum):
    """
    Visual themes available for a user profile.

    - LIGHT: Light theme.
    - DARK: Dark theme.
    """
    LIGHT = ('LIGHT', 'Light')
    DARK = ('DARK', 'Dark')

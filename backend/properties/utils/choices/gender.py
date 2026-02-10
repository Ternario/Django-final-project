from enum import Enum

from properties.utils.choices.enumMixin import ChoicesEnumMixin


class Gender(ChoicesEnumMixin, Enum):
    """
    Gender options for users in the system.

    - MALE: Male gender.
    - FEMALE: Female gender.
    - OTHER: Other  gender.
    """
    MALE = ('M', 'Male')
    FEMALE = ('F', 'Female')
    OTHER = ('O', 'Other')

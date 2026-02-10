from enum import Enum
from typing import List, Tuple

from django.utils.translation import gettext_lazy as _


class ChoicesEnumMixin(Enum):
    """Provides a `.choices()` method for Django model fields."""

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(item.value[0], _(item.value[1])) for item in cls]


class TimeEnumMixin(Enum):
    """Provides a `.choices()` method for Django model fields."""

    @classmethod
    def choices(cls) -> List[Tuple[str, str]]:
        return [(t.value, t.value.strftime('%H:%M')) for t in cls]

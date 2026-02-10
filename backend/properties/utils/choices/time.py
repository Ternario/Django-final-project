from enum import Enum
from datetime import time

from properties.utils.choices.enumMixin import TimeEnumMixin


class CheckInTime(TimeEnumMixin, Enum):
    """
    Allowed check-in times for properties.

    Each member represents an hour of the day when guests can check in.

    - _11AM: Check-in at 11:00 AM (default).
    - _12PM: Check-in at 12:00 PM.
    - _1PM: Check-in at 1:00 PM.
    - _2PM: Check-in at 2:00 PM.
    - _3PM: Check-in at 3:00 PM.
    - _4PM: Check-in at 4:00 PM.
    - _5PM: Check-in at 5:00 PM.
    - _6PM: Check-in at 6:00 PM.
    - _7PM: Check-in at 7:00 PM.
    - _8PM: Check-in at 8:00 PM.
    - _9PM: Check-in at 9:00 PM.
    - _10PM: Check-in at 10:00 PM.
    """
    _11AM = time(hour=11)
    _12PM = time(hour=12)
    _1PM = time(hour=13)
    _2PM = time(hour=14)
    _3PM = time(hour=15)
    _4PM = time(hour=16)
    _5PM = time(hour=17)
    _6PM = time(hour=18)
    _7PM = time(hour=19)
    _8PM = time(hour=20)
    _9PM = time(hour=21)
    _10PM = time(hour=22)

    @classmethod
    def default(cls):
        return cls._11AM.value


class CheckOutTime(TimeEnumMixin, Enum):
    """
    Allowed check-out times for properties.

    Each member represents an hour of the day when guests must check out.

    - _12AM: Check-out at 12:00 AM.
    - _1AM: Check-out at 1:00 AM.
    - _2AM: Check-out at 2:00 AM.
    - _3AM: Check-out at 3:00 AM.
    - _4AM: Check-out at 4:00 AM.
    - _5AM: Check-out at 5:00 AM.
    - _6AM: Check-out at 6:00 AM.
    - _7AM: Check-out at 7:00 AM.
    - _8AM: Check-out at 8:00 AM.
    - _9AM: Check-out at 9:00 AM.
    - _10AM: Check-out at 10:00 AM (default).
    """
    _10AM = time(hour=10)
    _9AM = time(hour=9)
    _8AM = time(hour=8)
    _7AM = time(hour=7)
    _6AM = time(hour=6)
    _5AM = time(hour=5)
    _4AM = time(hour=4)
    _3AM = time(hour=3)
    _2AM = time(hour=2)
    _1AM = time(hour=1)
    _12AM = time(hour=0)

    @classmethod
    def default(cls):
        return cls._10AM.value

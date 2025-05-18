from enum import Enum
from datetime import time
from django.utils.translation import gettext_lazy as _


class StatusEnumMixin:
    @classmethod
    def choices(cls):
        return [(status.name, _(status.value)) for status in cls]


class BookingStatus(StatusEnumMixin, Enum):
    PENDING = 'Pending'
    CONFIRMED = 'Confirmed'
    CANCELLED = 'Cancelled'
    COMPLETED = 'Completed'


class ReviewStatus(StatusEnumMixin, Enum):
    PUBLISHED = 'Published'
    FLAGGED = 'Flagged'
    REMOVED = 'Removed'


class TimeEnumMixin:
    @classmethod
    def choices(cls):
        return [{'value': t.value.strftime('%H:%M:%S'), 'label': t.value.strftime('%H:%M')} for t in cls]


class CheckInTime(TimeEnumMixin, Enum):
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

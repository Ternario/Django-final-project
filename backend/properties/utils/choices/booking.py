from enum import Enum

from properties.utils.choices.enumMixin import ChoicesEnumMixin


class BookingStatus(ChoicesEnumMixin, Enum):
    """
    Statuses of a properties in the system.

    - PENDING: Booking created but not yet confirmed.
    - CONFIRMED: Booking confirmed by the host or system.
    - CANCELLED: Booking cancelled by user or host.
    - COMPLETED: Booking period finished successfully.
    """

    PENDING = ('PENDING', 'Pending')
    CONFIRMED = ('CONFIRMED', 'Confirmed')
    CANCELLED = ('CANCELLED', 'Cancelled')
    COMPLETED = ('COMPLETED', 'Completed')


class CancellationPolicy(ChoicesEnumMixin, Enum):
    """
    Cancellation policies available for a booking.

    - FLEXIBLE: Free cancellation up to a short period before check-in.
    - MODERATE: Cancellation allowed with some conditions.
    - STRICT: Cancellation allowed with strict conditions or penalties.
    """
    FLEXIBLE = ('FLEXIBLE', 'Flexible')
    MODERATE = ('MODERATE', 'Moderate')
    STRICT = ('STRICT', 'Strict')

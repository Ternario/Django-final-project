from typing import Dict

from django.utils.translation import gettext_lazy as _

BOOKING_ERRORS: Dict[str, str] = {
    'empty': _('This field is required when properties is being cancelled.'),
    'length': _('Cancellation reason must be at least 30 characters long.'),
    'check_in_past': _('Start date cannot be in the past.'),
    'short_duration': _('The end date must be at least one day later than the start date.'),
    'overlaps_dates': _('This {property} is already reserved for the selected dates.'),
    'wrong_total_price': _('The total cost is calculated incorrectly.'),
    'status': _('This booking is already cancelled.'),
    'cancellation_permission': _('You cannot cancel your reservation.'),
    'user_cancellation': _('You cannot cancel the booking less than two days in advance.'),
    'cancellation_reason': _(
        'This field is required when booking is being cancelled and must be at least 40 characters long.'
    )
}

from typing import Dict

from django.utils.translation import gettext_lazy as _

REVIEW_ERRORS: Dict[str, str] = {
    'no_booking': _('You cannot write a review for apartments you did not booked.'),
    'active_booking': _('You cannot leave a review while the properties is active.'),
    'cancelled_before_start': _('You cannot write a review for bookings cancelled before they start.'),
    'duplicate': _('You have already left a comment for this reservation.'),
    'false_rating': _('The rating cannot be less than 1 and or greater than 5.'),
    'feedback_required': _('Please write a review if your rating is below 5.'),
    'rejected_reason': _('Please specify the reason for rejecting the review.'),
    'status': _('Action is not available.'),
    'owner_response': _('Owner response have contain from 10 to 2000 characters.')
}

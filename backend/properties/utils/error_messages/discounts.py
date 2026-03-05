from typing import Dict

from django.utils.translation import gettext_lazy as _

DISCOUNT_ERRORS: Dict[str, str] = {
    'past_valid_from': _('Start date (time) cannot be in the past.'),
    'short_duration': _('The end date (time) must be at least one day (hour) later than the start date (time).'),
    'currency': _('For fixed amounts, you must specify the currency.'),
    'expired_discount': _('The discount has already ended.'),
    'detail': _('Unexpected issues occurred while checking for discounts. Please try again later.'),
    'incompatible_with': _('You cannot add and remove the same Discount at once.'),
    'status': _('This user discount is already removed.'),
    'remove_reason': _(
        'This field is required when user discount is being removed and must be at least 40 characters long.'
    ),
    'already_active': _('This property discount is already active'),
    'already_inactive': _('This property discount is already inactive'),
    'seasonal': _('For seasonal discounts, you need to specify the start and end dates.'),
    'scheduled': _('For scheduled discounts, you need to specify the start and end dates.'),
    'both_fields': _('You need to specify both the start and end dates.'),
    'late_data_update': _('You cannot update discount data that was already activated.'),
    'permission': _('hash_id and discount_id must be provided to check discount permissions.')
}

DISCOUNT_PROPERTY_ERRORS: Dict[str, str] = {
    'owner': _('Property not mach to the owner.'),
    'discount_type': _('Referral or welcome Discount types is not applicable to properties.'),
    'discount_not_available': _('Discount not available.'),
    'discount_not_active': _('You cannot activate discount property model, discount not active.'),
    'discount_scheduled': _('You can only schedule or remove a model.'),
    'status': _('You cannot remove expired model.')

}

DISCOUNT_USER_ERRORS: Dict[str, str] = {
    'booking': _('No matched bookings found.')
}

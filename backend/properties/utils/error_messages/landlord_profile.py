from typing import Dict

from django.utils.translation import gettext_lazy as _

LANDLORD_PROFILE_ERRORS: Dict[str, str] = {
    'phone': _('The Phone Number must start with "+" and contain from 7 to 21 digits.'),
    'name': _('User full name and Landlord profile name must be the same.'),
    'type': _('Landlord Profile type must be specified.'),
    'landlord': _('You cannot perform this action on the selected object.'),
    'languages_spoken': _('You cannot add and remove the same language at once.'),
    'accepted_currencies': _('You cannot add and remove the same currency at once.'),
    'available_payment_methods': _('You cannot add and remove the same payment_method at once.')
}

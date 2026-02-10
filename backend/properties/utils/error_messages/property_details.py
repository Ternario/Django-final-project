from typing import Dict

from django.utils.translation import gettext_lazy as _

PROPERTY_DETAILS_ERRORS: Dict[str, str] = {
    'beds': _('At least one bed type is required.'),
    'total_beds': _('Total beds must equal sum of all bed types.'),
    'empty_floors': _('Floor number and total number of floors must be specified.'),
    'floor': _('Floor must be -1 (basement), 0, or between 1 and {total_floors}.')
}

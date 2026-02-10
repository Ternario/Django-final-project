from typing import Dict

from django.utils.translation import gettext_lazy as _

LOCATION_ERRORS: Dict[str, str] = {
    'data': _('No information found based on your data. Please re-check the details and try again.'),
    'field': _('The data in the field is incorrect.'),
    'confidence': _('The address you entered does not match. Please re-check the details and try again.')
}

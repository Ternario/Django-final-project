from typing import Dict

from django.utils.translation import gettext_lazy as _

PROPERTY_ERRORS: Dict[str, str] = {
    'no_landlord': _('Property must have either an individual or a company landlord.'),
    'both_landlords': _('Property cannot belong to both individual and company.'),
}

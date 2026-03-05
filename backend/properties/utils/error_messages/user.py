from typing import Dict

from django.utils.translation import gettext_lazy as _

USER_ERRORS: Dict[str, str] = {
    'password': _('Passwords do not match.'),
    'password_error': _('An error has occurred, please try again later.'),
    'date_of_birth': _('Registration is only permitted for people 18 years of age and older.'),
    'first_name': _('The First Name must be alphabet characters and can contain up to two dashes.'),
    'last_name': _('The Last Name must be alphabet characters and can contain up to two dashes.'),
    'phone': _('The Phone Number must start with "+" and contain from 7 to 21 digits'),
    'active_type': _('You profile already activated as landlord profile.'),
    'active_landlord': _(
        'You cannot change the landlord type while you still have old-type activ landlord profile.'
    ),
    'active_membership': _('You cannot activate your profile as landlord until you are activ company member user.'),
    'deactivate_landlord_profile': _(
        'You cannot deactivate your profile to regular type until you have active landlord profile(s).'
    ),
    'deactivate_membership': _(
        'You cannot deactivate your profile to regular type until you are activ company member user.'
    )
}

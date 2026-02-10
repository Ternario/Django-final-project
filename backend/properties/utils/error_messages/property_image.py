from typing import Dict

from django.utils.translation import gettext_lazy as _

PROPERTY_IMAGE_ERRORS: Dict[str, str] = {
    'request': _('Request param is required'),
    'max_amount': _('The maximum number of images cannot exceed 15.'),
    'limit': _('You have reached your image limit.'),
    'overlimit': _('You can add only {allowed_number} more image(s).'),
    'oversize': _('Each image must be smaller than 10 MB.'),
    'invalid_format': _('Image format must be one of the following: {formats}')
}

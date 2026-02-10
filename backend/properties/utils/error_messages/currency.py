from typing import Dict

CURRENCY_ERRORS: Dict[str, str] = {
    'conversion_rates': 'Failed to import/update currencies. Data is missing.',
    'default_data': 'Default currencies data is missing.',
    'success': 'Currencies imported/updated successfully!',
    'no_rate': 'No rate for {code} in API response.',
    'invalid_rate': 'Invalid rate for {code}: {rate_value}.'
}

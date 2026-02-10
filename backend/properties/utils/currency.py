import decimal
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from properties.models import User

import requests
from requests import Response

from decimal import Decimal, ROUND_HALF_UP

from base_config.settings import BASE_CURRENCY, EXCHANGERATE_API_KEY

from properties.models import Currency
from properties.utils.request_errors import ExternalServiceError


def get_default_currency() -> Currency:
    """
    Retrieve the default currency from the database, or create it if it does not exist.

    This function ensures that a Currency object with the code defined in BASE_CURRENCY
    exists. If it does not exist, it will be created with the following defaults:
        - code: BASE_CURRENCY (defined in the settings file)
        - name='Euro'
        - symbol='€'
        - rate_to_base=1

    Returns:
        Currency: An instance of the Currency model representing the default currency.
    """
    instance, _ = Currency.objects.get_or_create(code=BASE_CURRENCY, name='Euro', symbol='€', rate_to_base=1)
    return instance


def format_price(value: Decimal, rate: Decimal) -> decimal:
    """
    Convert a monetary value to a different currency using the specified rate
    and format it as a string with two decimal places, rounded half up.

    Args:
        value (Decimal): The original amount in base currency.
        rate (Decimal): The exchange rate to apply to the value.

    Returns:
        decimal: The formatted monetary value with two decimal places.
    """
    return (value * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def request_currency_rate() -> Dict[str, Any]:
    """
    Fetches the latest currency exchange rates from the external API.

    Returns:
        Dict[str, Any]: The full JSON response from the API, including a
        'conversion_rates' key with currency codes and their rates.

    Raises:
        ExternalServiceError: If the API request fails or returns an HTTP error.

    Notes:
        - Uses `requests.get` to query the API.
        - Intended for use by currency import/update commands or periodic rate updates.
    """
    try:
        response: Response = requests.get(
            f'https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest/{BASE_CURRENCY}', timeout=10
        )
        response.raise_for_status()

        return response.json()
    except requests.exceptions.RequestException as e:
        raise ExternalServiceError(f'Exchange Rate request failed: {e}')


def user_currency_or_default(request) -> Currency:
    """
    Retrieves the currency associated with the authenticated user, or falls back to a default.

    - If the request user is authenticated, returns `user.currency`.
    - If the user is not authenticated, attempts to get the currency by the
      `currency_code` query parameter (`?currency_code=XYZ`).
    - If the provided `currency_code` does not exist in the database,
      falls back to the system's `BASE_CURRENCY`.

    Args:
        request (HttpRequest): The current HTTP request object.

    Returns:
        Currency: A `Currency` model instance representing either the user's
        preferred currency or the default/base currency.

    Notes:
        - Designed for use in views or utilities where the current currency
          context is needed.
        - Ensures a valid Currency object is always returned for calculations
          or display purposes.
    """
    user: User = request.user

    if user.is_authenticated:
        currency: Currency = user.currency
    else:
        currency_code: str = request.GET.get('currency_code', BASE_CURRENCY)

        currency: Currency = Currency.objects.filter(
            code=currency_code
        ).first() or Currency.objects.get(code=BASE_CURRENCY)

    return currency

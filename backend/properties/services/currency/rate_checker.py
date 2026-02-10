from __future__ import annotations

import logging
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Dict, Any, List

from properties.models import Currency
from properties.utils.currency import request_currency_rate
from properties.utils.error_messages.currency import CURRENCY_ERRORS

logger = logging.getLogger(__name__)


class CurrencyRateChecker:
    """
    Updates currency exchange rates in the database based on external API data.

    Provides:
        - Fetching current exchange rates from a third-party service.
        - Validation of API response and logging of missing or invalid rates.
        - Conversion of rates to Decimal with 6 decimal places for precision.
        - Bulk updating of all Currency objects to minimize database queries.
    """

    @staticmethod
    def run() -> None:
        """
        Fetch exchange rates and update the `rate_to_base` field for all currencies.

        Notes:
            - Logs warnings for currencies missing in the API response.
            - Logs exceptions for invalid rate values or API request failures.
            - Intended for periodic execution (e.g., via Celery or cron).
        """
        try:
            results: Dict[str, Any] = request_currency_rate()
        except Exception as e:
            logger.exception(e)
            return

        if not results.get('conversion_rates', None):
            logger.exception(CURRENCY_ERRORS['conversion_rates'])
            return

        rates: Dict[str, float | int] = results['conversion_rates']

        currencies_to_update: List[Currency] = []

        for currency in Currency.objects.all():
            code: str = currency.code
            rate_value: float | int = rates.get(currency.code)

            if rate_value is None:
                logger.warning(CURRENCY_ERRORS['no_rate'].format(code=code))
                continue

            try:
                rate_to_base = Decimal(rate_value).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
            except (InvalidOperation, ValueError):
                logger.exception(CURRENCY_ERRORS['invalid_rate'].format(code=code, rate_value=rate_value))
                continue

            currency.rate_to_base = rate_to_base
            currencies_to_update.append(currency)

        Currency.objects.bulk_update(currencies_to_update, ['rate_to_base'])

from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Dict, Any, List

from django.core.management.base import BaseCommand

from properties.models import Currency
from properties.utils.currency import request_currency_rate
from properties.utils.error_messages.currency import CURRENCY_ERRORS


class Command(BaseCommand):
    """
    Imports currencies from a JSON file and updates their exchange rates using an external API.

    Provides:
        - Fetching current exchange rates from a third-party service.
        - Loading default currency data from a JSON file.
        - Validation of API response and logging of missing or invalid rates.
        - Creation of new Currency objects or updating existing ones with precise rates.
    """
    help: str = 'Import currencies from JSON file and update rates from API'

    def handle(self, *args, **kwargs) -> None:
        """
        Execute the import and update process.

        Notes:
            - Logs warnings for currencies missing in the API response.
            - Logs warnings for invalid rate values that cannot be converted to Decimal.
            - Outputs success or failure messages to the console.
            - Intended to be run manually or scheduled via management commands.
        """
        results: Dict[str, Any] = request_currency_rate()

        if not results.get('conversion_rates', None):
            self.stdout.write(self.style.ERROR(CURRENCY_ERRORS['conversion_rates']))
            return

        rates: Dict[str, float | int] = results['conversion_rates']

        with open('properties/fixtures/base_currencies.json', 'r', encoding='utf-8') as f:
            currencies_default_data: List[Dict[str, str]] = json.load(f)

            if not currencies_default_data:
                self.stdout.write(self.style.ERROR(CURRENCY_ERRORS['default_data']))
                return

        for currency in currencies_default_data:
            code: str = currency['code']
            rate_value: float | int = rates.get(code)

            if rate_value is None:
                self.stdout.write(self.style.WARNING(CURRENCY_ERRORS['no_rate'].format(code=code)))
                continue

            try:
                rate_to_base = Decimal(rate_value).quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
            except (InvalidOperation, ValueError):
                self.stdout.write(
                    self.style.WARNING(CURRENCY_ERRORS['invalid_rate'].format(code=code, rate_value=rate_value))
                )
                continue

            Currency.objects.update_or_create(
                code=code,
                defaults={
                    'name': currency['name'],
                    'symbol': currency.get('symbol', ''),
                    'rate_to_base': rate_to_base
                }
            )

        self.stdout.write(self.style.SUCCESS(CURRENCY_ERRORS['success']))

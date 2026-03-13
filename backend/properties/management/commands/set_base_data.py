from __future__ import annotations

import os
import subprocess
import sys
from typing import Dict, Any, List

import json
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from base_config.settings import BASE_DIR
from properties.models import Currency

from properties.utils.currency import request_currency_rate
from properties.utils.error_messages.currency import CURRENCY_ERRORS


class Command(BaseCommand):
    """
    Load static fixtures and update currency rates from an external API.

    This management command performs two main tasks:
        1. Loads static data from JSON fixtures (e.g., amenities, locations) into the database.
        2. Updates currency exchange rates from a third-party API.
           - Reads base currency data from a JSON file.
           - Creates new Currency objects or updates existing ones with precise Decimal rates.

    Notes:
        - Can be run manually via manage.py or scheduled as a recurring task.
        - Provides colored console output for easy monitoring.
    """
    help: str = 'Load initial data from fixtures and update currency rates from API'

    def _load_fixtures(self) -> None:
        """
        Load base data from JSON fixtures into the database.

        Iterates over predefined fixture files (amenities.json, locations.json, etc.) and:
            - Loads each fixture using Django's loaddata command.
            - Logs success or failure  messages for each file.
        """

        fixture_files = [
            'languages.json', 'users.json', 'landlord_profiles.json', 'amenities.json', 'cancellation_policies.json',
            'locations.json', 'payment_methods.json', 'payment_types.json', 'properties.json', 'discounts.json',
            'discount_properties.json'
        ]

        for fixture_file in fixture_files:
            try:
                call_command('loaddata', fixture_file, verbosity=0)
                self.stdout.write(self.style.SUCCESS(f'Load fixture: {fixture_file}... OK'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to load fixture {fixture_file}: {e}'))

    def _update_currencies(self) -> None:
        """
        Fetch current currency rates from the API and update the Currency model.

        Steps:
            - Load default currency codes from a JSON fixture.
            - Request latest exchange rates from an external API.
            - Log warnings for missing or invalid rates.
            - Create or update Currency objects with precise Decimal rates.
        """

        results: Dict[str, Any] = request_currency_rate()

        if not results.get('conversion_rates', None):
            self.stdout.write(self.style.ERROR(CURRENCY_ERRORS['conversion_rates']))
            return

        rates: Dict[str, float | int] = results['conversion_rates']

        with open('properties/fixtures/currencies.json', 'r', encoding='utf-8') as f:
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

        self.stdout.write(self.style.SUCCESS('Load and update: currencies.json... OK'))

    def handle(self, *args, **kwargs) -> None:
        from properties.services.discount.status_checker import CheckDiscountStatus
        """
        Execute the full data import and currency update process.

        Steps:
            1. Load static fixtures into the database using `_load_fixtures()`.
            2. Update currency rates from the external API using `_update_currencies()`.

        Notes:
            - Provides clear output for success, warning, and error messages.
            - Designed to be run as a management command via manage.py.
        """

        fixtures_build_path: str = os.path.join(BASE_DIR, 'properties', 'fixtures', 'generators', 'build.py')

        subprocess.run([sys.executable, fixtures_build_path], check=True)

        self._update_currencies()
        self._load_fixtures()

        CheckDiscountStatus().check_expire(now(), True)
        CheckDiscountStatus().check_activation(now(), True)

        self.stdout.write(self.style.SUCCESS(f'Update linked discounts and discount_properties... OK'))

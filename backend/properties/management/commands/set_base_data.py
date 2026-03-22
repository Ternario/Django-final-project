from __future__ import annotations

import os
import subprocess
import sys
from typing import Dict, Any, List

import json
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils.timezone import now
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from base_config.settings import BASE_DIR
from properties.management.commands.utils import celery_tasks, build_minute_expr
from properties.models import User, Currency

from properties.utils.currency import request_currency_rate
from properties.utils.error_messages.currency import CURRENCY_ERRORS


class Command(BaseCommand):
    """
    Load static fixtures, update currency rates, and create Celery tasks.

    This management command performs the following main actions:

    1. Load static JSON fixtures into the database:
        - Examples: amenities, locations, users, discounts, discount_properties, etc.
        - Uses Django's `loaddata` command for each fixture file.

    2. Update currency exchange rates:
        - Reads base currency data from a JSON fixture.
        - Requests latest exchange rates from an external API.
        - Creates or updates Currency objects with precise Decimal rates.

    3. Create or update Celery periodic tasks and schedules:
        - Generates `CrontabSchedule` objects based on task intervals and offsets.
        - Creates or updates `PeriodicTask` objects linked to these schedules.
        - Ensures tasks are not duplicated by checking unique 'name'.

    Notes:
        - Can be run manually via `manage.py set_base_data`.
        - Supports optional `--force` flag to skip database existence checks.
        - Provides console output for easy monitoring of success, warnings, and errors.
    """
    help: str = 'Load initial data from fixtures and update currency rates from API'

    def add_arguments(self, parser: Any) -> None:
        """
        Add command-line arguments for the management command.

        Args:
            parser: ArgumentParser instance to which arguments are added.

        Adds the following option:
            --force : Skip database existence checks and reload all data including Celery tasks,
                      even if tables or users already exist.
        """
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip database existence checks and reload data anyway.'
        )

    def _create_celery_tasks(self) -> None:
        """
        Create or update Celery periodic tasks in the database.

        This includes:
            - Creating `CrontabSchedule` objects based on task intervals and offsets.
            - Creating or updating `PeriodicTask` objects linked to these schedules.
            - Ensures tasks are not duplicated by checking unique 'name'.

        Used internally by the management command to setup all scheduled tasks.
        """
        raw_tasks_data: List[Dict[str, str | int]] = celery_tasks.copy()

        for task in raw_tasks_data:
            minute, minute_offset, task, hour = (task['minute'], task['minute_offset'], task['task'], task['hour'])

            schedule, _ = CrontabSchedule.objects.get_or_create(
                minute=build_minute_expr(minute, minute_offset),
                hour=hour,
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
                timezone='UTC',
            )

            PeriodicTask.objects.get_or_create(
                name=f'{task}-every-{minute}-minutes-offset-{minute_offset}',
                task=task,
                crontab=schedule
            )

        self.stdout.write(self.style.SUCCESS(f'Create Celery tasks... OK'))

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
        """
        Execute the full data import, currency update, and Celery task creation process.

        Steps:
            1. Create or update Celery periodic tasks using `_create_celery_tasks()`.
            2. Update currency rates from the external API using `_update_currencies()`.
            3. Load static fixtures into the database using `_load_fixtures()`.

        Notes:
            - Provides clear output for success, warning, and error messages.
            - Designed to be run as a management command via manage.py.
            - Supports optional `--force` flag to skip DB existence checks.
        """
        from properties.services.discount.status_checker import CheckDiscountStatus

        if not kwargs.get('force', False):
            with connection.cursor() as cursor:
                cursor.execute("SHOW TABLES LIKE 'django_migrations';")
                table_exists = cursor.fetchone()

            if not table_exists:
                self.stdout.write(self.style.WARNING("Migrations not applied yet"))
                return

            if User.objects.exists():
                self.stdout.write(self.style.SUCCESS("Data already initialized"))
                return

        self.stdout.write(self.style.WARNING('Loading initial data...'))

        fixtures_build_path: str = os.path.join(BASE_DIR, 'properties', 'fixtures', 'generators', 'build.py')

        subprocess.run([sys.executable, fixtures_build_path], check=True)

        self._create_celery_tasks()
        self._update_currencies()
        self._load_fixtures()

        CheckDiscountStatus().check_expire(now(), True)
        CheckDiscountStatus().check_activation(now(), True)

        self.stdout.write(self.style.SUCCESS(f'Update linked discounts and discount_properties... OK'))

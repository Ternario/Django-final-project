from __future__ import annotations

from copy import deepcopy
from datetime import datetime
from typing import List, Dict, Any, Set

import sys
import django
import os

import json
import logging

from discounts import discounts
from data_templates.users_and_landlord_profiles import user_profiles_data
from data_templates.discounts import seasonal_discounts, owner_promo_discounts
from data_templates.amenities import amenity_data
from amenities import amenities
from data_templates.cancellation_policies import cancellation_policy_data
from cancellation_policies import cancellation_policies
from data_templates.currencies import currency_data
from data_templates.locations import locations_data
from locations import locations
from data_templates.languages import language_data
from data_templates.payment_methods import payment_method_data
from languages import languages
from payment_methods import payment_methods
from data_templates.payment_types import payment_type_data
from payment_types import payment_types
from discount_property import discount_properties

from utils import user_type, set_personal_data
from users import users
from landlord_profiles import profiles, members
from property import properties

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../../../'))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'base_config.settings')

django.setup()

date: str = datetime.now().isoformat() + 'Z'

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)

u_p_d: Dict[str, List[Dict[str, str] | List[Dict[str, Any]]]] = deepcopy(user_profiles_data)

users_in_data_map_count: int = 0

for k, v in user_profiles_data.items():
    if k in ['superusers', 'admins', 'individuals']:
        users_in_data_map_count += len(v)

    else:
        for v2 in v:
            users_in_data_map_count += 1

            for i in v2['profiles']:
                users_in_data_map_count += len(i['members'])

total_user_count: int = users_in_data_map_count

count_of_simple_users: int = 6

for i in range(users_in_data_map_count + 1, users_in_data_map_count + count_of_simple_users):
    email: str = f'user{i - users_in_data_map_count}@example.com'
    first_name: str = 'Simple'
    last_name: str = f'User{i - users_in_data_map_count}'
    landlord_type: str = 'NONE'
    u_p_d['simple_users'].append({
        'email': email, 'first_name': first_name, 'last_name': last_name, 'landlord_type': landlord_type
    })
    total_user_count += 1

superusers: List[Dict[str, str]] = u_p_d['superusers']
admins: List[Dict[str, str]] = u_p_d['admins']
individuals: List[Dict[str, str]] = u_p_d['individuals']
companies: List[Dict[str, Any]] = u_p_d['companies']
simple_users: List[Dict[str, Any]] = u_p_d['simple_users']

u_type: dict[int, str] = user_type.copy()

amenities_raw_data: List[Dict[str, Any]] = amenity_data.copy()
cancellation_policy_raw_data: List[Dict[str, Any]] = cancellation_policy_data.copy()
currency_raw_data: List[Dict[str, str]] = currency_data.copy()
locations_raw_data: List[Dict[str, str | List[str]]] = locations_data.copy()
languages_raw_data: List[Dict[str, str]] = language_data.copy()
payment_method_raw_data: List[Dict[str, str]] = payment_method_data.copy()
payment_type_raw_data: List[Dict[str, str]] = payment_type_data.copy()


def build_fixtures():
    """
    Generates project JSON fixtures from predefined template data.

    The function compiles fixture data for multiple system entities such as
    amenities, cancellation policies, currencies, locations, languages,
    payment methods, and payment types.

    It also generates relational domain data including users, landlord profiles
    (individual and company), company memberships, properties, discounts,
    and discount–property relations.

    User records are created from template datasets (superusers, admins,
    individual landlords, company landlords with members, and simple users).
    Personal data such as phone numbers and passwords are generated dynamically.
    Landlord profiles and properties are generated per user according to the
    template configuration, and discounts may be attached both globally
    (seasonal) and per landlord (owner promotions).

    Seasonal and owner discounts can be linked to generated properties through
    discount-property relations.

    Finally, all compiled data structures are serialized into JSON files and
    written to the `properties/fixtures` directory, so they can be loaded into
    the database as Django fixtures.
    """
    from base_config.settings import HASH_SALT

    salt: str = HASH_SALT

    amenity_fixtures: List[Dict[str, Any]] = []
    cancellation_policy_fixtures: List[Dict[str, Any]] = []
    currency_fixtures: List[Dict[str, Any]] = []
    location_fixtures: List[Dict[str, Any]] = []
    language_fixtures: List[Dict[str, Any]] = []
    payment_method_fixtures: List[Dict[str, Any]] = []
    payment_type_fixtures: List[Dict[str, Any]] = []

    user_fixtures: List[Dict[str, Any]] = []
    landlord_profile_fixtures: List[Dict[str, Any]] = []
    property_fixtures: List[Dict[str, Any]] = []
    discount_fixtures: List[Dict[str, Any]] = []
    discount_property_fixtures: List[Dict[str, Any]] = []

    current_amenity_category_index: int = 1
    current_amenity_index: int = 1
    current_cancellation_policy_index: int = 1
    current_country_index: int = 1
    current_city_index: int = 1
    current_language_index: int = 1
    current_payment_method_index: int = 1
    current_payment_type_index: int = 1

    current_user_index: int = 1
    current_landlord_profile_index: int = 1
    current_membership_index: int = 1
    current_property_index: int = 1
    current_discount_index: int = 1
    current_discount_property_index: int = 1

    total_seasonal_discounts_count: int = 0

    countries_and_citizenship: List[str] = []

    faker_location_map: Dict[str, Dict[str, Any]] = {}

    for amenity in amenities_raw_data:
        a_index, amenity_list = amenities(current_amenity_category_index, current_amenity_index, amenity, date)
        amenity_fixtures.extend(amenity_list)

        current_amenity_category_index += 1
        current_amenity_index += a_index

    logger.info('Compile amenities... OK')

    for cp in cancellation_policy_raw_data:
        cancellation_policy_fixtures.append(
            cancellation_policies(current_cancellation_policy_index, cp, date)
        )

        current_cancellation_policy_index += 1

    logger.info('Compile cancellation policies... OK')

    for currency in currency_raw_data:
        currency_fixtures.append({
            'code': currency['code'],
            'name': currency['name'],
            'symbol': currency['symbol']
        })

    logger.info('Compile currencies... OK')

    for loc in locations_raw_data:
        current_city_index, country_cities_map, location_list = locations(
            current_country_index, current_city_index, loc, date
        )
        location_fixtures.extend(location_list)

        countries_and_citizenship.append(country_cities_map['country'])
        faker_location_map[country_cities_map['country']] = {
            'c_index': country_cities_map['index'],
            'code': f'{country_cities_map["code"].lower()}_{country_cities_map["code"]}',
            'phone': country_cities_map['phone'],
            'cities': country_cities_map['cities']
        }

        current_country_index += 1
        current_city_index += current_city_index

    logger.info('Compile locations... OK')

    for language in languages_raw_data:
        language_fixtures.append(languages(current_language_index, language, date))
        current_language_index += 1

    logger.info('Compile languages... OK')

    for p_method in payment_method_raw_data:
        payment_method_fixtures.append(payment_methods(current_payment_method_index, p_method, date))
        current_payment_method_index += 1

    logger.info('Compile payment_methods... OK')

    for p_type in payment_type_raw_data:
        payment_type_fixtures.append(payment_types(current_payment_type_index, p_type, date))
        current_payment_type_index += 1

    logger.info('Compile payment_types... OK')

    for superuser in superusers:
        has_discounts: bool = superuser.get('has_discounts', False)
        user_t: str = u_type[1]
        password, phone = set_personal_data(current_user_index)
        superuser['phone'] = phone

        user_fixtures.extend(users(current_user_index, user_t, superuser, password, date, countries_and_citizenship))
        if has_discounts:
            raw_discounts: List[Dict[str, Any]] = seasonal_discounts

            for discount in raw_discounts:
                discount_fixtures.append(discounts(current_discount_index, current_user_index, discount, date))

                current_discount_index += 1
                total_seasonal_discounts_count += 1

        current_user_index += 1

    logger.info('Compile superusers... OK')

    for admin in admins:
        has_discounts: bool = admin.get('has_discounts', False)
        user_t: str = u_type[2]
        password, phone = set_personal_data(current_user_index)
        admin['phone'] = phone

        user_fixtures.extend(users(current_user_index, user_t, admin, password, date, countries_and_citizenship))
        if has_discounts:
            raw_discounts: List[Dict[str, Any]] = seasonal_discounts

            for discount in raw_discounts:
                discount_fixtures.append(discounts(current_discount_index, current_user_index, discount, date))

                current_discount_index += 1
                total_seasonal_discounts_count += 1

        current_user_index += 1

    logger.info('Compile admins... OK')

    for individual in individuals:
        has_discounts: bool = individual.pop('owner_discounts', False)
        apply_seasonal_discounts: bool = individual.pop('apply_seasonal_discounts', False)
        prop_number: int = individual.pop('prop_number', 0)
        user_t: str = u_type[3]
        password, phone = set_personal_data(current_user_index)
        individual['phone'] = phone

        user_fixtures.extend(users(current_user_index, user_t, individual, password, date, countries_and_citizenship))

        lp_data: Dict[str, Any] = {
            'p_index': current_landlord_profile_index,
            'u_index': current_user_index,
            'salt': salt,
            'landlord_type': individual['landlord_type'],
            'first_name': individual['first_name'],
            'last_name': individual['last_name'],
        }

        profile_country, profile = profiles(date, countries_and_citizenship, faker_location_map, lp_data)
        landlord_profile_fixtures.append(profile)

        owner_discounts_map: Set[int] = set()

        if has_discounts:
            raw_discounts: List[Dict[str, Any]] = deepcopy(owner_promo_discounts)

            for discount in raw_discounts:
                discount['name'] = f'{discount["name"]} landlord {current_landlord_profile_index}'
                discount['landlord_profile'] = current_landlord_profile_index
                discount_fixtures.append(discounts(current_discount_index, current_user_index, discount, date))

                owner_discounts_map.add(current_discount_index)

                current_discount_index += 1

        for i_prop in range(prop_number):
            property_fake_location: Dict[str, Any] = {
                'name': profile_country,
                'c_index': faker_location_map[profile_country]['c_index'],
                'code': faker_location_map[profile_country]['code'],
                'cities': faker_location_map[profile_country]['cities'],
            }

            property_fixtures.extend(
                properties(
                    current_property_index, current_landlord_profile_index, current_user_index, date,
                    property_fake_location
                )
            )

            if apply_seasonal_discounts and total_seasonal_discounts_count > 0:
                for s_discount in range(1, total_seasonal_discounts_count + 1):
                    discount_property_fixtures.append(
                        discount_properties(
                            current_discount_property_index, s_discount, current_property_index,
                            current_landlord_profile_index,
                            current_user_index, date
                        )
                    )

                    current_discount_property_index += 1

            if has_discounts and owner_discounts_map:
                for ow_index, value in enumerate(owner_discounts_map):
                    discount_property_fixtures.append(
                        discount_properties(
                            current_discount_property_index, value, current_property_index,
                            current_landlord_profile_index, current_user_index, date
                        )
                    )

                    current_discount_property_index += 1

            current_property_index += 1

        current_user_index += 1
        current_landlord_profile_index += 1

    logger.info('Compile individual_landlords... OK')

    for company in companies:
        user_model: Dict[str, str] = company['user_model']
        has_discounts: bool = user_model.pop('owner_discounts', False)

        profiles_data: List[Dict[str, int | bool | List[Dict[str, str]]]] = company['profiles']

        user_t: str = u_type[3]
        password, phone = set_personal_data(current_user_index)
        user_model['phone'] = phone

        user_fixtures.extend(users(current_user_index, user_t, user_model, password, date, countries_and_citizenship))

        company_owner_user_index: int = current_user_index

        current_user_index += 1

        for profile in profiles_data:
            profile_number: int = profile['number']
            apply_seasonal_discounts: bool = profile.pop('apply_seasonal_discounts', False)
            prop_number: int = profile.pop('prop_number', 0)

            lp_data: Dict[str, Any] = {
                'p_index': current_landlord_profile_index,
                'u_index': company_owner_user_index,
                'salt': salt,
                'landlord_type': user_model['landlord_type'],
                'first_name': user_model['first_name'],
                'last_name': user_model['last_name'],
                'c_number': profile_number
            }
            profile_country, profile_obj = profiles(date, countries_and_citizenship, faker_location_map, lp_data)
            landlord_profile_fixtures.append(profile_obj)

            property_fake_location: Dict[str, Any] = {
                'name': profile_country,
                'c_index': faker_location_map[profile_country]['c_index'],
                'code': faker_location_map[profile_country]['code'],
                'cities': faker_location_map[profile_country]['cities'],
            }

            owner_discounts_map: Set[int] = set()

            if has_discounts:
                raw_discounts: List[Dict[str, Any]] = deepcopy(owner_promo_discounts)

                for discount in raw_discounts:
                    discount['name'] = f'{discount["name"]} landlord {current_landlord_profile_index}'
                    discount['landlord_profile'] = current_landlord_profile_index
                    discount_fixtures.append(
                        discounts(current_discount_index, company_owner_user_index, discount, date))

                    owner_discounts_map.add(current_discount_index)

                    current_discount_index += 1

            for i_prop in range(prop_number):
                property_fixtures.extend(
                    properties(
                        current_property_index, current_landlord_profile_index, current_user_index, date,
                        property_fake_location
                    )
                )
                if apply_seasonal_discounts and total_seasonal_discounts_count > 0:
                    for s_discount in range(1, total_seasonal_discounts_count + 1):
                        discount_property_fixtures.append(
                            discount_properties(
                                current_discount_property_index, s_discount, current_property_index,
                                current_landlord_profile_index,
                                company_owner_user_index, date
                            )
                        )

                        current_discount_property_index += 1

                if has_discounts and owner_discounts_map:
                    for ow_index, value in enumerate(owner_discounts_map):
                        discount_property_fixtures.append(
                            discount_properties(
                                current_discount_property_index, value, current_property_index,
                                current_landlord_profile_index, company_owner_user_index, date
                            )
                        )

                        current_discount_property_index += 1

                current_property_index += 1

            for member in profile['members']:
                role: str = member.pop('role', 'ACCOUNTANT')
                user_t: str = u_type[3]
                password, phone = set_personal_data(current_user_index)
                member['phone'] = phone

                user_fixtures.extend(
                    users(current_user_index, user_t, member, password, date, countries_and_citizenship))

                cm_data: Dict[str, Any] = {
                    'm_index': current_membership_index,
                    'c_index': current_landlord_profile_index,
                    'u_index': current_user_index,
                    'first_name': member['first_name'],
                    'last_name': member['last_name'],
                    'role': role
                }

                landlord_profile_fixtures.append(
                    members(date, cm_data, faker_location_map[property_fake_location['name']]['phone'])
                )
                current_user_index += 1

                current_membership_index += 1

            current_landlord_profile_index += 1

    logger.info('Compile company_landlords... OK')

    for user in simple_users:
        user_t: str = u_type[3]
        password, phone = set_personal_data(current_user_index)
        user['phone'] = phone

        user_fixtures.extend(users(current_user_index, user_t, user, password, date, countries_and_citizenship))
        current_user_index += 1

    with open('properties/fixtures/amenities.json', 'w') as f:
        json.dump(amenity_fixtures, f, indent=2)

    logger.info('Create fixture: amenities.json... OK')

    with open('properties/fixtures/cancellation_policies.json', 'w') as f:
        json.dump(cancellation_policy_fixtures, f, indent=2)

    logger.info('Create fixture: cancellation_policies.json... OK')

    with open('properties/fixtures/locations.json', 'w') as f:
        json.dump(location_fixtures, f, indent=2)

    logger.info('Create fixture: locations.json... OK')

    with open('properties/fixtures/currencies.json', 'w') as f:
        json.dump(currency_fixtures, f, indent=2)

    logger.info('Create fixture: currencies.json... OK')

    with open('properties/fixtures/languages.json', 'w') as f:
        json.dump(language_fixtures, f, indent=2)

    logger.info('Create fixture: languages.json... OK')

    with open('properties/fixtures/payment_methods.json', 'w') as f:
        json.dump(payment_method_fixtures, f, indent=2)

    logger.info('Create fixture: payment_methods.json... OK')

    with open('properties/fixtures/payment_types.json', 'w') as f:
        json.dump(payment_type_fixtures, f, indent=2)

    logger.info('Create fixture: payment_types.json... OK')

    with open('properties/fixtures/users.json', 'w') as f:
        json.dump(user_fixtures, f, indent=2)

    logger.info('Create fixture: users.json... OK')

    with open('properties/fixtures/landlord_profiles.json', 'w') as f:
        json.dump(landlord_profile_fixtures, f, indent=2)

    logger.info('Create fixture: landlord_profiles.json... OK')

    with open('properties/fixtures/properties.json', 'w') as f:
        json.dump(property_fixtures, f, indent=2)

    logger.info('Create fixture: properties.json... OK')

    with open('properties/fixtures/discount_properties.json', 'w') as f:
        json.dump(discount_property_fixtures, f, indent=2)

    logger.info('Create fixture: discount_properties.json... OK')

    with open('properties/fixtures/discounts.json', 'w') as f:
        json.dump(discount_fixtures, f, indent=2)

    logger.info('Create fixture: discounts.json... OK')


build_fixtures()

from __future__ import annotations

import hashlib

from datetime import timedelta, datetime
from typing import Dict, Any, List

import random


def profiles(
        date: str, countries: List[str], f_locations: Dict[str, Any], lp_date: Dict[str, Any]
) -> (str, Dict[str, Any]):
    p_index, u_index, landlord_type, first_name, last_name, c_number = (
        lp_date['p_index'], lp_date['u_index'], lp_date['landlord_type'], lp_date['first_name'],
        lp_date['last_name'], lp_date.get('c_number', None)
    )

    minutes: int = c_number if c_number else 0
    raw_string: str = f'{datetime.fromisoformat(date) + timedelta(minutes=minutes)}-{lp_date["salt"]}-{u_index}'

    hash_id: str = hashlib.sha256(raw_string.encode()).hexdigest()[:12]

    country: str = random.choice(countries)
    city: str = random.choice(f_locations[country]['cities'])['name']
    phone_prefix: str = f_locations[country]['phone']

    if landlord_type == 'INDIVIDUAL':
        name: str = f'{first_name} {last_name}'
        email: str = f'{first_name.lower()}.{last_name.lower()}-{p_index}@example.com'
        phone: str = f'{phone_prefix}{random.randint(1000000000, 9999999999)}'
        tax_id: str = f'IND-TAX-{random.randint(1000, 9999)}'
        registration_address: str = (
            f'{country}, {city}, {random.randint(1, 100)} Street'
        )
        description: str = (
            f'Private landlord {first_name} {last_name} managing apartments for long-term comfortable living.'
        )
        is_trusted: bool = False
    else:
        name: str = f'{first_name} {last_name} Company-{c_number}'
        email: str = f'{first_name.lower()}.{last_name.lower()}-{p_index}-{c_number}@example.com'
        phone: str = f'{phone_prefix}{random.randint(1000000000, 9999999999)}'
        tax_id: str = f'COM-TAX{random.randint(10000000, 99999999)}'
        registration_address: str = (
            f'{country}, {city}, {random.randint(1, 100)} Business Tower'
        )
        description: str = (
            f'Professional company {first_name} {last_name} managing residential and commercial properties.'
        )
        is_trusted: bool = True

    profile: Dict[str, Any] = {
        'model': 'properties.landlordprofile',
        'pk': p_index,
        'fields': {
            'hash_id': hash_id,
            'created_by': u_index,
            'name': name,
            'phone': phone,
            'email': email,
            'type': landlord_type,
            'tax_id': tax_id,
            'registration_address': registration_address,
            'description': description,
            'default_currency': 1,
            'is_verified': True,
            'is_trusted': is_trusted,
            'is_deleted': False,
            'languages_spoken': [1],
            'accepted_currencies': [1],
            'available_payment_methods': [1],
            'created_at': date,
            'updated_at': date,
        }
    }

    return country, profile


def members(date: str, cm_data: Dict[str, Any],phone_prefix: str) -> Dict[str, Any]:
    c_index, u_index, first_name, last_name = (
        cm_data['c_index'], cm_data['u_index'], cm_data['first_name'], cm_data['last_name']
    )

    email: str = f'{first_name.lower()}.{last_name.lower()}-{c_index}-{u_index}@example.com'
    phone: str = f'{phone_prefix}{random.randint(1000000000, 9999999999)}'

    return {
        'model': 'properties.companymembership',
        'pk': cm_data['m_index'],
        'fields': {
            'company': c_index,
            'user': u_index,
            'user_full_name': f'{first_name} {last_name}',
            'phone': phone,
            'email': email,
            'role': cm_data['role'],
            'languages_spoken': [1],
            'joined_at': date,
            'is_active': True,
            'is_deleted': False,
            'created_at': date,
            'updated_at': date,
        }
    }

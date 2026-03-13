from __future__ import annotations
from typing import List, Dict, Any

import random

from django.contrib.auth.hashers import make_password

from utils import user_type


def users(
        index: int, u_type: str, data: Dict[str, str], password: str, date: str, citizenships: List[str]
) -> List[Dict[str, Any]]:
    fixtures: List[Dict[str, Any]] = []

    email, first_name, last_name, phone = (data['email'], data['first_name'], data['last_name'], data['phone'])

    landlord_type: str = data.get('landlord_type', 'NONE')

    password: str = make_password(password)

    user_fields: Dict[str, Any] = {
        'email': email,
        'password': password,
        'first_name': first_name,
        'last_name': last_name,
        'language': 1,
        'currency': 1,
        'is_active': True,
        'date_joined': date,
        'created_at': date,
        'updated_at': date,
    }

    if u_type == user_type[1]:
        user_fields.update({
            'is_staff': True,
            'is_superuser': True,
            'is_admin': True,
            'is_moderator': False,
            'is_landlord': False,
            'landlord_type': landlord_type,
            'is_verified': True,
            'is_deleted': False,
        })
    elif u_type == user_type[2]:
        user_fields.update({
            'is_staff': True,
            'is_superuser': False,
            'is_admin': True,
            'is_moderator': False,
            'is_landlord': False,
            'landlord_type': landlord_type,
            'is_verified': True,
            'is_deleted': False,
        })
    else:
        user_fields.update({
            'is_landlord': True if landlord_type != 'NONE' else False,
            'landlord_type': landlord_type,
            'is_verified': True,
            'is_deleted': False,
        })

    fixtures.append({
        'model': 'properties.user',
        'pk': index,
        'fields': user_fields
    })

    fixtures.append({
        'model': 'properties.userprofile',
        'pk': index,
        'fields': {
            'user': index,
            'phone': phone,
            'gender': 'M' if index % 2 else 'F',
            'citizenship': random.choice(citizenships),
            'theme': 'LIGHT',
            'receive_email_notifications': True,
            'receive_push_notifications': True,
            'created_at': date,
            'updated_at': date
        }
    })

    return fixtures

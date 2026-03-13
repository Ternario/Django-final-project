from __future__ import annotations

from typing import Dict, Any


def discounts(d_index: int, u_index: int, data: Dict[str, Any], date: str) -> Dict[str, Any]:
    return {
        'model': 'properties.discount',
        'pk': d_index,
        'fields': {
            'created_by': u_index,
            'is_admin_created': data.get('is_admin_created', False),
            'landlord_profile': data.get('landlord_profile', None),
            'name': data['name'],
            'description': data['description'],
            'type': data['type'],
            'value_type': data['value_type'],
            'currency': data.get('currency', 1),
            'value': data['value'],
            'priority': data['priority'],
            'valid_from': data.get('valid_from', ''),
            'valid_until': data.get('valid_until', ''),
            'stack_policy': data['stack_policy'],
            'incompatible_with': data.get('incompatible_with', []),
            'status': data['status'],
            'created_at': date,
            'updated_at': date,
        }
    }

from typing import Dict, Any


def payment_types(pt_index: int, data: Dict[str, str], date: str) -> Dict[str, Any]:
    return {
        'model': 'properties.paymenttype',
        'pk': pt_index,
        'fields': {
            'code': data['code'],
            'name': data['name'],
            'created_at': date,
            'updated_at': date
        }
    }

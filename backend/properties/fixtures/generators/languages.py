from __future__ import annotations

from typing import  Dict, Any


def languages(l_index: int, data: Dict[str, str], date: str) -> Dict[str, Any]:
    return {
        'model': 'properties.language',
        'pk': l_index,
        'fields': {
            'code': data['code'],
            'name': data['name'],
            'created_at': date,
            'updated_at': date
        }
    }

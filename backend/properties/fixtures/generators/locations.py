from __future__ import annotations

from typing import List, Dict, Any


def locations(country_index: int, c_index: int, data: Dict[str, str | List[str]], date: str) -> (
        int, Dict[str, Any], List[Dict[str, Any]]
):
    country_cities_map: Dict[str, str | List[Dict[str, Any]]] = {
        'country': data['country'],
        'index': country_index,
        'code': data['code'],
        'phone': data['phone'],
        'cities': []
    }

    fixtures: List[Dict[str, str]] = [{
        'model': 'properties.country',
        'pk': country_index,
        'fields': {
            'name': data['country'],
            'code': data['code'],
            'created_at': date,
            'updated_at': date
        }
    }]

    index: int = c_index

    for city in data['cities']:
        fixtures.append({
            'model': 'properties.city',
            'pk': index,
            'fields': {
                'name': city,
                'country': country_index,
                'created_at': date,
                'updated_at': date
            }
        })

        country_cities_map['cities'].append({
            'index': index,
            'name': city
        })

        index += 1

    return index, country_cities_map, fixtures

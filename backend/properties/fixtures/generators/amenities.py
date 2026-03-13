from typing import List, Dict


def amenities(c_index: int, a_index: int, data: Dict[str, str], date: str, ) -> (int, List[Dict[str, str]]):
    fixtures: List[Dict[str, str]] = [{
        'model': 'properties.amenitycategory',
        'pk': c_index,
        'fields': {
            'name': data['category_name'],
            'created_at': date,
            'updated_at': date
        }
    }]

    index: int = a_index

    for amenity in data['amenities']:
        fixtures.append({
            'model': 'properties.amenity',
            'pk': index,
            'fields': {
                'name': amenity,
                'category': c_index,
                'created_at': date,
                'updated_at': date
            }
        })

        index += 1

    return index, fixtures

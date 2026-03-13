from typing import Dict, Any


def discount_properties(
        dp_index: int, d_index: int, p_index: int, lp_index: int, added_by: int, date: str
) -> Dict[str, Any]:
    return {
        'model': 'properties.discountproperty',
        'pk': dp_index,
        'fields': {
            'discount': d_index,
            'property_ref': p_index,
            'landlord_profile': lp_index,
            'added_by': added_by,
            'status': 'SCHEDULED',
            'created_at': date,
            'updated_at': date
        }
    }

from typing import List, Dict


def cancellation_policies(cp_index: int, cp_data: Dict[str, List[Dict[str, str]]], date: str) -> Dict[str, str]:
    return {
        'model': 'properties.cancellationpolicy',
        'pk': cp_index,
        'fields': {
            'name': cp_data['name'],
            'type': cp_data['type'],
            'description': cp_data['description'],
            'free_cancellation_days': cp_data['free_cancellation_days'],
            'refund_percentage_after_deadline': cp_data['refund_percentage_after_deadline'],
            'created_at': date,
            'updated_at': date
        }
    }

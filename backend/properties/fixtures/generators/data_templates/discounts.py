from calendar import monthrange
from datetime import datetime, timezone
from typing import Dict, List, Any

date: datetime = datetime.now(timezone.utc)

feb_last_day = monthrange(date.year + 1, 2)[1]


def parse_iso(date_str: str):
    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))


def get_discount_status(valid_from: str, valid_until: str):
    start: datetime = parse_iso(valid_from)
    end: datetime = parse_iso(valid_until)

    if date < start:
        return 'SCHEDULED'
    elif start <= date <= end:
        return 'ACTIVE'
    else:
        return 'EXPIRED'


date_discount_statuses: Dict[str, Dict[str, str]] = {
    'spring': {
        'valid_from': f'{date.year}-03-01T00:00:00Z',
        'valid_until': f'{date.year}-05-31T23:59:59Z',
    },
    'summer': {
        'valid_from': f'{date.year}-06-01T00:00:00Z',
        'valid_until': f'{date.year}-08-31T23:59:59Z',
    },
    'winter': {
        'valid_from': f'{date.year}-12-01T00:00:00Z',
        'valid_until': f'{date.year + 1}-02-{feb_last_day}T23:59:59Z',
    },
    'autumn': {
        'valid_from': f'{date.year}-09-01T00:00:00Z',
        'valid_until': f'{date.year}-11-30T23:59:59Z',
    },
}

seasonal_discounts: List[Dict[str, Any]] = [
    {
        'is_admin_created': True,
        'name': 'Summer',
        'description': 'Summer booking discount.',
        'type': 'SEASONAL',
        'value_type': 'PERCENTAGE',
        'currency': 1,
        'value': '15.00',
        'priority': 90,
        'valid_from': date_discount_statuses['summer']['valid_from'],
        'valid_until': date_discount_statuses['summer']['valid_until'],
        'stack_policy': 'STACKABLE',
        'incompatible_with': [],
        # 'status': get_discount_status(
        #     date_discount_statuses['summer']['valid_from'], date_discount_statuses['summer']['valid_until'],
        # )
        'status': 'SCHEDULED'
    },
    {
        'is_admin_created': True,
        'name': 'Winter',
        'description': 'Winter seasonal discount.',
        'type': 'SEASONAL',
        'value_type': 'PERCENTAGE',
        'currency': 1,
        'value': '20.00',
        'priority': 90,
        'valid_from': date_discount_statuses['winter']['valid_from'],
        'valid_until': date_discount_statuses['winter']['valid_until'],
        'stack_policy': 'STACKABLE',
        'incompatible_with': [],
        # 'status': get_discount_status(
        #     date_discount_statuses['winter']['valid_from'], date_discount_statuses['winter']['valid_until']
        # )
        'status': 'SCHEDULED'
    },
    {
        'is_admin_created': True,
        'name': 'Spring',
        'description': 'Seasonal spring promotion.',
        'type': 'SEASONAL',
        'value_type': 'PERCENTAGE',
        'currency': 1,
        'value': '15.00',
        'priority': 90,
        'valid_from': date_discount_statuses['spring']['valid_from'],
        'valid_until': date_discount_statuses['spring']['valid_until'],
        'stack_policy': 'STACKABLE',
        'incompatible_with': [],
        # 'status': get_discount_status(
        #     date_discount_statuses['spring']['valid_from'], date_discount_statuses['spring']['valid_until']
        # )
        'status': 'SCHEDULED'
    },
    {
        'is_admin_created': True,
        'name': 'Autumn Weekend',
        'description': 'Autumn weekend seasonal offer.',
        'type': 'SEASONAL',
        'value_type': 'PERCENTAGE',
        'currency': 1,
        'value': '12.50',
        'priority': 90,
        'valid_from': date_discount_statuses['autumn']['valid_from'],
        'valid_until': date_discount_statuses['autumn']['valid_until'],
        'stack_policy': 'STACKABLE',
        'incompatible_with': [],
        # 'status': get_discount_status(
        #     date_discount_statuses['autumn']['valid_from'], date_discount_statuses['autumn']['valid_until']
        # )
        'status': 'SCHEDULED'
    }
]

owner_promo_discounts: List[Dict[str, Any]] = [
    {
        'is_admin_created': False,
        'name': 'Owner promo',
        'description': 'Owner promo discount',
        'type': 'OWNER_PROMO',
        'value_type': 'FIXED',
        'currency': 1,
        'value': '25.00',
        'priority': 70,
        'valid_from': f'{date.year}-01-01T00:00:00Z',
        'valid_until': f'{date.year}-12-31T23:59:59Z',
        'stack_policy': 'TYPE_EXCLUSIVE',
        'incompatible_with': [],
        'status': 'ACTIVE'
    }
]

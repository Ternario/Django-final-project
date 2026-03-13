from __future__ import annotations

from decimal import Decimal
from random import randint, choice, sample
from typing import Dict, Any, List

from faker import Faker


def properties(
        p_id: int, o_id: int, u_id: int, date: str, property_fake_location: Dict[str, Any]
) -> List[Dict[str, Any]]:
    fake = Faker(property_fake_location['code'])
    fake_text = Faker('en_US')

    fixtures: List[Dict[str, Any]] = []

    base_price: Decimal = Decimal(randint(30, 300))
    taxes: Decimal = Decimal(randint(0, 50))
    total_price: Decimal = base_price + taxes
    discounted_price: Decimal = total_price
    title = f'{fake_text.unique.sentence(nb_words=4).rstrip(".")} {o_id}'

    fixtures.append({
        'model': 'properties.property',
        'pk': p_id,
        'fields': {
            'owner': o_id,
            'created_by': u_id,
            'title': title,
            'slug': title.replace(' ', '-'),
            'description': fake_text.text(max_nb_chars=300),
            'property_type': choice(['APARTMENT', 'HOUSE', 'STUDIO', 'VILLA', 'PENTHOUSE', 'HOSTEL', 'HOTEL']),
            'base_price': str(base_price),
            'taxes_fees': str(taxes),
            'total_price': str(total_price),
            'discounted_price': str(discounted_price),
            'min_stay': randint(1, 5),
            'max_guests': randint(1, 8),
            'rating': '4.5',
            'review_count': 12,
            'cancellation_policy': 1,
            'house_rules': fake.text(max_nb_chars=200),
            'status': 'ACTIVE',
            'approval_status': choice(['AUTO_APPROVED', 'MANUAL_APPROVED']),
            'auto_confirm_bookings': fake.boolean(),
            'is_deleted': False,
            'amenities': sample(range(1, 30), randint(3, 4)),
            'payment_types': sample(range(1, 4), randint(1, 3)),
            'created_at': date,
            'updated_at': date
        }
    })

    single_beds: int = randint(1, 3)
    double_beds: int = randint(0, 3)
    sofa_beds: int = randint(0, 3)
    total_beds: int = sofa_beds + double_beds + single_beds

    fixtures.append({
        'model': 'properties.propertydetail',
        'pk': p_id,
        'fields': {
            'property_ref': p_id,
            'property_area': str(Decimal(randint(25, 200))),
            'floor': randint(1, 5),
            'total_floors': 5,
            'number_of_rooms': randint(1, 4),
            'total_beds': total_beds,
            'single_beds': single_beds,
            'double_beds': double_beds,
            'sofa_beds': sofa_beds,
            'number_of_bathrooms': randint(1, 3),
            'shower': fake.boolean(),
            'bathtub': fake.boolean(),
            'toilet': fake.boolean(),
            'bathroom_access': 'private',
            'kitchen': fake.boolean(),
            'kitchen_access': 'private',
            'num_balcony': 1,
            'terrace': fake.boolean(),
            'terrace_access': 'private',
            'garden': fake.boolean(),
            'garden_access': 'private',
            'check_in_from': '14:00:00',
            'check_out_until': '11:00:00',
            'created_at': date,
            'updated_at': date
        }
    })

    fixtures.append({
        'model': 'properties.location',
        'pk': p_id,
        'fields': {
            'property_ref': p_id,
            'country': property_fake_location['c_index'],
            'city': choice(property_fake_location['cities'])['index'],
            'post_code': fake.postcode(),
            'street': fake.street_name(),
            'house_number': fake.building_number(),
            'created_at': date,
            'updated_at': date
        }
    })

    return fixtures

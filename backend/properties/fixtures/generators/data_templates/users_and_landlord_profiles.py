from __future__ import annotations

from typing import Dict, List, Any

user_profiles_data: Dict[str, List[Dict[str, str] | List[Dict[str, Any]]]] = {
    'superusers': [
        {'email': 'superuser1@example.com', 'first_name': 'Site', 'last_name': 'Superuser1'}
    ],
    'admins': [
        {'email': 'admin1@example.com', 'first_name': 'Site', 'last_name': 'Admin1', 'has_discounts': True}
    ],
    'individuals': [
        {
            'email': 'individual1@example.com', 'first_name': 'Individual', 'last_name': 'Landlord1',
            'landlord_type': 'INDIVIDUAL', 'owner_discounts': True, 'prop_number': 10, 'apply_seasonal_discounts': True
        },
        {
            'email': 'individual2@example.com', 'first_name': 'Individual', 'last_name': 'Landlord2',
            'landlord_type': 'INDIVIDUAL', 'prop_number': 13
        },
        {
            'email': 'individual3@example.com', 'first_name': 'Individual', 'last_name': 'Landlord3',
            'landlord_type': 'INDIVIDUAL', 'owner_discounts': True, 'prop_number': 9
        }
    ],
    'companies': [
        {
            'user_model': {'email': 'company1@example.com', 'first_name': 'Company', 'last_name': 'Owner1',
                           'landlord_type': 'COMPANY', 'owner_discounts': True},
            'profiles': [
                {
                    'number': 1,
                    'prop_number': 10,
                    'apply_seasonal_discounts': False,
                    'members': [
                        {'email': 'member1@example.com', 'first_name': 'Member', 'last_name': 'One', 'role': 'ADMIN',
                         'landlord_type': 'COMPANY_MEMBER'},
                        {'email': 'member2@example.com', 'first_name': 'Member', 'last_name': 'Two', 'role': 'MANAGER',
                         'landlord_type': 'COMPANY_MEMBER'},
                    ]
                }
            ]
        },
        {
            'user_model': {'email': 'company2@example.com', 'first_name': 'Company', 'last_name': 'Owner2',
                           'landlord_type': 'COMPANY'},
            'profiles': [
                {
                    'number': 1,
                    'prop_number': 6,
                    'apply_seasonal_discounts': True,
                    'members': [

                        {'email': 'member3@example.com', 'first_name': 'Member', 'last_name': 'Three', 'role': 'ADMIN',
                         'landlord_type': 'COMPANY_MEMBER'},
                        {'email': 'member4@example.com', 'first_name': 'Member', 'last_name': 'Four', 'role': 'MANAGER',
                         'landlord_type': 'COMPANY_MEMBER'},
                    ]
                },
                {
                    'number': 2,
                    'prop_number': 10,
                    'apply_seasonal_discounts': True,
                    'members': [

                        {'email': 'member5@example.com', 'first_name': 'Member', 'last_name': 'Five', 'role': 'ADMIN',
                         'landlord_type': 'COMPANY_MEMBER'},
                        {'email': 'member6@example.com', 'first_name': 'Member', 'last_name': 'Six', 'role': 'MANAGER',
                         'landlord_type': 'COMPANY_MEMBER'},
                    ]
                },
            ]
        }
    ],
    'simple_users': []
}

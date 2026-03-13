from __future__ import annotations

from typing import Dict, List

amenity_data: List[Dict[str, str | List[str]]] = [
    {
        'category_name': 'Basic',
        'amenities': [
            'Wi-Fi', 'Heating', 'Air Conditioning', 'Hot Water', 'Smoke Detector', 'Fire Extinguisher',
            '24-hour Reception'
        ]
    },
    {
        'category_name': 'Facilities',
        'amenities': [
            'Parking', 'Elevator', 'Wheelchair Accessible', 'Luggage Storage', 'Shared Lounge/TV Area', 'Laundry',
            'Room Service'
        ]
    },
    {
        'category_name': 'Food & Drink',
        'amenities': [
            'Restaurant', 'Bar', 'Breakfast Available', 'Coffee/Tea Maker', 'Mini Bar', 'Vending Machine'
        ]
    },
    {
        'category_name': 'Wellness',
        'amenities': [
            'Swimming Pool', 'Fitness Center', 'Spa', 'Hot Tub/Jacuzzi', 'Steam Room', 'Yoga Classes'
        ]
    },
    {
        'category_name': 'Services',
        'amenities': [
            'Concierge', 'Airport Shuttle', 'Car Rental', 'Ticket Service', 'Wake-up Service', 'Newspapers'
        ]
    },
    {
        'category_name': 'Entertainment',
        'amenities': [
            'TV', 'Video Games', 'Library', 'Live Music', 'Game Room'
        ]
    },

]

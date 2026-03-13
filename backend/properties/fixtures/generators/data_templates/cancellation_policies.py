from __future__ import annotations

from typing import Dict, List

cancellation_policy_data: List[Dict[str, str | int]] = [
    {
        'name': 'Flexible Standard',
        'type': 'FLEXIBLE',
        'description': 'Allows free cancellation up to 24 hours before check-in without any penalty.',
        'free_cancellation_days': 1,
        'refund_percentage_after_deadline': 50.0
    },
    {
        'name': 'Flexible Extended',
        'type': 'FLEXIBLE',
        'description': 'Guests can cancel up to 3 days before check-in and get full refund.',
        'free_cancellation_days': 3,
        'refund_percentage_after_deadline': 25.0
    },
    {
        'name': 'Moderate Standard',
        'type': 'MODERATE',
        'description': 'Guests can cancel up to 5 days before check-in for full refund. After that, 50% refund.',
        'free_cancellation_days': 5,
        'refund_percentage_after_deadline': 50.0
    },
    {
        'name': 'Moderate Extended',
        'type': 'MODERATE',
        'description': 'Cancellation allowed up to 7 days before check-in. After deadline, 30% refund.',
        'free_cancellation_days': 7,
        'refund_percentage_after_deadline': 30.0
    },
    {
        'name': 'Strict Standard',
        'type': 'STRICT',
        'description': 'Cancellation allowed only up to 14 days before check-in. No refund after deadline.',
        'free_cancellation_days': 14,
        'refund_percentage_after_deadline': 0.0
    },
    {
        'name': 'Strict Extended',
        'type': 'STRICT',
        'description': 'Guests must cancel at least 21 days in advance to get any refund. Otherwise, no refund.',
        'free_cancellation_days': 21,
        'refund_percentage_after_deadline': 0.0
    }

]

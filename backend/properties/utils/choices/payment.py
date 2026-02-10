from enum import Enum

from properties.utils.choices.enumMixin import ChoicesEnumMixin


class PaymentType(ChoicesEnumMixin, Enum):
    """
    Methods or timing of payment for a booking.

    - IMMEDIATE: Payment is required immediately at the time of booking.
    - ON_ARRIVAL: Payment is made upon arrival at the property.
    - DEPOSIT: Partial payment (deposit) is made in advance.
    """
    IMMEDIATE = ('IMMEDIATE', 'Immediate')
    ON_ARRIVAL = ('ON_ARRIVAL', 'On arrival')
    DEPOSIT = ('DEPOSIT', 'Deposit')


class PaymentStatus(ChoicesEnumMixin, Enum):
    """
    Status of a payment for a booking.

    - PENDING: Payment is pending and has not been completed yet.
    - SUCCESS: Payment has been successfully completed.
    - FAILED: Payment attempt has failed.
    - REFUNDED: Payment has been refunded to the customer.
    """
    PENDING = ('PENDING', 'Pending')
    SUCCESS = ('SUCCESS', 'Success')
    FAILED = ('FAILED', 'Failed')
    REFUNDED = ('REFUNDED', 'Refunded')

from enum import Enum

from properties.utils.choices.enumMixin import ChoicesEnumMixin


class DiscountStatus(ChoicesEnumMixin, Enum):
    """
    Represents the lifecycle states of a discount within the system.

    - DRAFT: The discount is created but not yet active or published.
    - SCHEDULED: The discount has been created, but the activation date has not yet arrived.
    - ACTIVE: The discount is currently valid and can be applied.
    - EXPIRED: The discount has passed its validity period and can no longer be used.
    - DISABLED: The discount has been manually deactivated or suspended.
    """
    DRAFT = ('DRAFT', 'Draft')
    SCHEDULED = ('SCHEDULED', 'Scheduled')
    ACTIVE = ('ACTIVE', 'Active')
    EXPIRED = ('EXPIRED', 'Expired')
    DISABLED = ('DISABLED', 'Disabled')
    ARCHIVED = 'ARCHIVED', 'Archived'


class DiscountUserStatus(ChoicesEnumMixin, Enum):
    """
    Represents the lifecycle states of a DiscountUser instance.

    - SCHEDULED: The DiscountUser record has been created, but the user has not yet received the discount.
    - ACTIVE: The discount has been assigned to the user and is currently valid for use.
    - USED: The discount has already been applied by the user.
    - EXPIRED: The discount has passed its validity period and can no longer be used.
    - REMOVED: The discount has been manually removed or invalidated for the user.
    """
    SCHEDULED = ('SCHEDULED', 'Scheduled')
    ACTIVE = ('ACTIVE', 'Active')
    USED = ('USED', 'Used')
    EXPIRED = ('EXPIRED', 'Expired')
    REMOVED = ('REMOVED', 'Removed')


class DiscountType(ChoicesEnumMixin, Enum):
    """
    Defines the different types or sources of discounts available in the system.

    - SEASONAL: A discount applied during specific seasons or promotional periods.
    - COUPON: A discount that requires a coupon or promo code to activate.
    - REFERRAL: A discount granted through a referral or invitation program.
    - CUSTOM: A discount applicable under specific conditions.
    """
    SEASONAL = ('SEASONAL', 'Seasonal')
    COUPON = ('COUPON', 'Coupon')
    REFERRAL = ('REFERRAL', 'Referral')
    WELCOME = ('WELCOME ', 'Welcome')
    CUSTOM = ('CUSTOM', 'Custom')


class DiscountValueType(ChoicesEnumMixin, Enum):
    """
    Value types of discounts that can be applied to a booking or property.

    - PERCENTAGE: Discount represented as a percentage of the total price.
    - FIXED: Discount represented as a fixed monetary amount.
    """
    PERCENTAGE = ('PERCENTAGE', 'Percentage')
    FIXED = ('FIXED', 'Fixed')

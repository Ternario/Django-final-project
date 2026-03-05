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
    Represents the different types or sources of discounts in the system.

    Public discounts (affect list prices for properties):
      - SEASONAL: Applied during specific seasons or promotional periods.
      - OWNER_PROMO: Set manually by a property owner/landlord for one or more properties.

    Private / user-specific discounts (do not affect general property list prices):
      - COUPON: Requires a coupon or promo code to activate.
      - REFERRAL: Granted through a referral or invitation program.
      - WELCOME: Applied to new users as a welcome promotion.
      - COMPENSATION: Granted to specific users, e.g., as a refund or compensation.
    """
    SEASONAL = ('SEASONAL', 'Seasonal')
    OWNER_PROMO = ('OWNER_PROMO', 'Owner promo')
    COUPON = ('COUPON', 'Coupon')
    REFERRAL = ('REFERRAL', 'Referral')
    WELCOME = ('WELCOME ', 'Welcome')
    COMPENSATION = ('COMPENSATION', 'Compensation')


class DiscountValueType(ChoicesEnumMixin, Enum):
    """
    Value types of discounts that can be applied to a booking or property.

    - PERCENTAGE: Discount represented as a percentage of the total price.
    - FIXED: Discount represented as a fixed monetary amount.
    """
    PERCENTAGE = ('PERCENTAGE', 'Percentage')
    FIXED = ('FIXED', 'Fixed')


class DiscountStackPolicy(ChoicesEnumMixin, Enum):
    """
    Defines how a discount behaves when combined with other discounts.

    - STACKABLE: Can be combined with other discounts and applied together.
    - EXCLUSIVE: Cannot be combined with any other discount.
    - TYPE_EXCLUSIVE: Cannot be combined with other discounts of the same type,
      but may be combined with discounts of different types.
    """
    STACKABLE = ('STACKABLE', 'Stackable')
    EXCLUSIVE = ('EXCLUSIVE', 'Exclusive')
    TYPE_EXCLUSIVE = ('TYPE_EXCLUSIVE', 'Type exclusive')


class DiscountPropertyStatus(ChoicesEnumMixin, Enum):
    """
    Represents the lifecycle status of a discount assigned to a property.

    - SCHEDULED: The discount is planned and will become active at a future date.
    - ACTIVE: The discount is currently active and applied to the property.
    - EXPIRED: The discount has reached its end date and is no longer active.
    - REMOVED: The discount property was manually removed or deactivated before expiration.
    """
    SCHEDULED = ('SCHEDULED', 'Scheduled')
    ACTIVE = ('ACTIVE', 'Active')
    EXPIRED = ('EXPIRED', 'Expired')
    REMOVED = ('REMOVED', 'Removed')

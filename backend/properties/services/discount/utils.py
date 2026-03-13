from typing import List

from properties.utils.choices.discount import DiscountType

DISCOUNT_APPLICATION_ORDER: List[str] = [
    DiscountType.SEASONAL.value[0],
    DiscountType.PROMO.value[0],
    DiscountType.OWNER_PROMO.value[0],
    DiscountType.COUPON.value[0],
    DiscountType.COMPENSATION.value[0],
]

DISCOUNTS_BATCH_SIZE: int = 1000

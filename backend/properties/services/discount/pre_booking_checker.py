from decimal import Decimal, ROUND_HALF_UP
from typing import Set, List, Dict, Tuple

from django.db.models import Q
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError

from properties.models import Discount, Property, Currency
from properties.utils.choices.discount import (
    DiscountStackPolicy, DiscountPropertyStatus, DiscountValueType, DiscountStatus
)
from properties.utils.error_messages.booking import BOOKING_ERRORS


class PreBookingChecker:
    """
    Service class for validating and calculating discounts for a Property
    booking request.

    This class implements logic to:
        - Fetch all active Discount objects specified by IDs.
        - Validate discount compatibility based on stack policies:
            * Exclusive: cannot be combined with any other discounts.
            * Type-exclusive: cannot be combined with other discounts of the same type.
            * Stackable: can be combined unless explicitly incompatible.
        - Validate that all provided discount IDs are valid for the property.
        - Calculate the final discounted price based on selected discounts
          (percentage or fixed amount).
        - Return both the validated Discount objects and the calculated price.

    Designed for use in:
        - Booking creation or pre-booking validation.
        - Ensuring business rules for discounts are enforced before saving
          a booking instance.
    """
    _EXCLUSIVE: str = DiscountStackPolicy.EXCLUSIVE.value[0]
    _TYPE_EXCLUSIVE: str = DiscountStackPolicy.TYPE_EXCLUSIVE.value[0]

    def __init__(self, prop_instance: Property, discount_ids: List[int], currency: Currency):
        self.prop_instance = prop_instance
        self.discount_ids = discount_ids
        self.currency = currency

    def _get_discount_list(self) -> List[Discount]:
        """
        Validate the provided discounts and check compatibility rules.

        Validation rules:
            - All provided discount IDs must exist and be active for the property.
            - Only one Exclusive discount can be applied.
            - Exclusive discounts cannot be combined with any other discounts.
            - Type-exclusive discounts cannot be combined with other discounts
              of the same type.
            - Stackable discounts cannot be combined with explicitly incompatible discounts.

        Raises:
            ValidationError: If any validation rule is violated.

        Returns:
            List[Discount]: List of validated Discount objects that can be applied.
        """
        discounts: Set[int] = set(self.discount_ids)

        discount_list: List[Discount] = list(
            Discount.objects.filter(
                pk__in=discounts, status=DiscountStatus.ACTIVE.value[0], valid_until__gte=now()
            ).filter(
                Q(is_admin_created=True) |
                Q(
                    discount_properties__property_ref_id=self.prop_instance.pk,
                    discount_properties__status=DiscountPropertyStatus.ACTIVE.value[0]
                )
            ).prefetch_related('incompatible_with')
        )

        if len(discount_list) != len(discounts):
            raise ValidationError({'applied_discounts': BOOKING_ERRORS['invalid_discounts']})

        exclusive_count: int = sum(
            1 for i in discount_list if i.stack_policy == self._EXCLUSIVE
        )

        if exclusive_count >= 1 and len(discount_list) > 1:
            raise ValidationError({'non_field_errors': BOOKING_ERRORS['exclusive_discounts']})

        discounts_ids: Set[int] = {d.pk for d in discount_list}

        incompatibility_map: Dict[int, Set[int]] = {
            d.pk: {inc.pk for inc in d.incompatible_with.all() if inc.pk in discounts_ids} for d in
            discount_list
        }

        for i, disc_1 in enumerate(discount_list):
            for disc_2 in discount_list[i + 1:]:
                if (
                        disc_1.stack_policy == self._TYPE_EXCLUSIVE and
                        disc_2.stack_policy == self._TYPE_EXCLUSIVE and
                        disc_1.type == disc_2.type
                ):
                    raise ValidationError({'non_field_errors': BOOKING_ERRORS['incompatible_types_discounts']})

                if (
                        disc_1.pk in incompatibility_map[disc_2.pk] or
                        disc_2.pk in incompatibility_map[disc_1.pk]
                ):
                    raise ValidationError({'non_field_errors': BOOKING_ERRORS['incompatible_discounts']})
        return discount_list

    def _calculate_price(self, discount_list: List[Discount]) -> Decimal:
        """
        Calculate the final discounted price based on the validated discounts.

        Discounts are applied in the following way:
            - Percentage discounts reduce the total price by the given percent.
            - Fixed discounts reduce the total price by the specified amount.
            - The resulting price is rounded to 2 decimal places using
              ROUND_HALF_UP.

        Args:
            discount_list (List[Discount]): List of validated Discount objects.

        Returns:
            Decimal: The final discounted price after applying all discounts.
        """
        total_price: Decimal = self.prop_instance.total_price
        discounts_value: Decimal = Decimal('0.00')

        for discount in discount_list:
            if discount.value_type == DiscountValueType.PERCENTAGE.value[0]:
                discounts_value += total_price * Decimal(discount.value) / Decimal('100')
            else:
                discounts_value += Decimal(discount.value)

        return (total_price - discounts_value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def execute(self) -> Tuple[List[Discount], Decimal]:
        """
        Main entry point to validate discounts and compute discounted price.

        Steps:
            - Validate the provided discounts using `_get_discount_list`.
            - Calculate the discounted price using `_calculate_price`.

        Returns:
            Tuple[List[Discount], Decimal]:
                - List of validated Discount objects.
                - Calculated discounted price for the booking.

        Raises:
            ValidationError: If any discount validation rule is violated.
        """

        discount_list: List[Discount] = self._get_discount_list()

        discounted_price: Decimal = self._calculate_price(discount_list)

        return discount_list, discounted_price

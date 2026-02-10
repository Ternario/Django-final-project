from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Set, Tuple, Any

if TYPE_CHECKING:
    from properties.models import User, Property, Currency

import logging
from decimal import Decimal

from django.db.models import Q, QuerySet
from django.utils import timezone

from properties.models import Discount
from properties.services.discount.calculator.base import BaseCalculator
from properties.utils.choices.discount import DiscountType, DiscountStatus, DiscountUserStatus
from properties.utils.error_messages.discounts import DISCOUNT_ERRORS

logger = logging.getLogger(__name__)


class DiscountCalculator(BaseCalculator):
    """
    Concrete discount calculator for a single Property instance.

    This class extends `BaseCalculator` and implements all logic required to:
        - Retrieve discounts applicable to a specific property and, optionally, a user.
        - Separate discounts into base (price-affecting) and other categories.
        - Select the best applicable discount based on saving, priority, and
          minimum price rules.
        - Compute final and base prices with optional currency conversion.
        - Provide compatibility information between discounts.

    Applicable discounts include:
        - Discounts directly linked to the property.
        - Discounts assigned to a specific user (if user is provided).

    Attributes:
        user (User | None):
            User for whom discounts are being evaluated. Some discounts may apply
            only to specific users. If None, only property-based discounts are considered.
        instance (Property):
            Property for which price calculation is performed.
        base_price (Decimal):
            Base property price including taxes and fees.
    """

    def __init__(self, user: User | None, instance: Property, currency: Currency | None) -> None:
        super().__init__(currency)
        self.user = user
        self.instance = instance
        self.base_price: Decimal = self._get_base_price(instance)

    def _request_discounts(self) -> QuerySet[Discount]:
        """
        Retrieve all discounts applicable to the property and, if user is provided, to the user.

        Applies filtering by:
            - active status,
            - validity period,
            - discounts linked to the property,
            - discounts linked to the user if a user is provided.

        Returns:
            QuerySet[Discount]:
                Filtered queryset of discounts relevant to this calculation.
        """
        now = timezone.now()

        discount_queryset: QuerySet[Discount] = Discount.objects.filter(
            status=DiscountStatus.ACTIVE.value[0],
            discount_properties__property_id=self.instance.pk,
            discount_properties__is_active=True,
        ).filter(
            Q(valid_from__isnull=True) | Q(valid_from__lte=now),
            Q(valid_until__isnull=True) | Q(valid_until__gte=now)
        )

        if not self.user:
            return discount_queryset.distinct()

        return discount_queryset.filter(
            discount_users__user_id=self.user.pk,
            discount_users__status=DiscountUserStatus.ACTIVE.value[0]
        ).filter(
            Q(discount_users__expires_at__isnull=True) | Q(discount_users__expires_at__gte=now),
        ).distinct()

    @staticmethod
    def _filter_applied_discount(discount_list: QuerySet[Discount]) -> Tuple[List[Discount], List[Discount]]:
        """
        Split discounts into base (price-affecting) and other (informational) categories.

        Base discounts include:
            - Seasonal
            - Referral

        Args:
            discount_list (QuerySet[Discount]):
                Discounts returned by `_request_discounts()`.

        Returns:
            Tuple[List[Discount], List[Discount]]:
                A tuple of two lists:
                (base_discounts, other_discounts)
        """
        if not discount_list:
            return [], []

        base_discounts: List[Discount] = []
        other_discounts: List[Discount] = []

        for discount in discount_list:
            if discount.type in [DiscountType.SEASONAL.value[0], DiscountType.REFERRAL.value[0]]:
                base_discounts.append(discount)
            else:
                other_discounts.append(discount)

        return base_discounts, other_discounts

    @staticmethod
    def _set_compatibility_map(discount_list: QuerySet[Discount]) -> Dict[int, Set[int]]:
        """
        Build a mapping of discounts to incompatible discount IDs.

        For each discount in the input list that has incompatible relations,
        this method collects the IDs of discounts it is marked as incompatible with.

        Only discounts with incompatible relations are included in the resulting dictionary.

        Args:
            discount_list (QuerySet[Discount]):
                Discounts returned by `_request_discounts()`.

        Returns:
            Dict[int, Set[int]]:
                A dictionary where keys are discount IDs and values are sets of discount IDs
                that are incompatible with the key discount.
        """
        incompatibility_map: Dict[int, Set[int]] = {}

        for discount in discount_list:
            if discount.compatible:
                incompatible_ids = set(d.id for d in discount.incompatible_with.all())

                if incompatible_ids:
                    incompatibility_map[discount.pk] = incompatible_ids

        return incompatibility_map

    def calculate(self) -> Dict[str, Any]:
        """
        Perform full discount calculation for a single property.

        Workflow:
            1. Retrieve all applicable discounts.
            2. If no discounts exist → return base price.
            3. Separate base and non-base discounts.
            4. Compute compatibility mapping between discounts.
            5. Select the best base discount according to saving / priority rules.
            6. Calculate final price (with currency conversion if enabled).
            7. Produce a structured result with all pricing details.

        Returns:
            Dict[str, Any]:
                {
                    'final_price': Decimal,
                    'base_price': Decimal,
                    'base_discounts': List[Discount],
                    'other_discounts': List[Discount],
                    'current_discount': Discount | None,
                    'incompatible_with': Dict[int, Set[int]],
                    'detail': str
                }

        Error Handling:
            Any unexpected exception is logged and a fallback response with base
            price and error detail is returned.
        """
        try:
            discount_list: QuerySet[Discount] = self._request_discounts()

            if not discount_list.exists():
                final_price: Decimal = self.base_price
                final_price = self._convert_final_price(final_price)

                return {
                    'final_price': final_price,
                    'base_price': final_price,
                    'base_discounts': [],
                    'other_discounts': [],
                    'current_discount': None,
                    'incompatible_with': {},
                    'detail': ''
                }

            base_discounts, other_discounts = self._filter_applied_discount(discount_list)
            incompatible_with: Dict[int, Set[int]] = self._set_compatibility_map(discount_list)

            best_discount: Discount | None = self._set_base_discount(self.base_price, base_discounts)
            final_price: Decimal = self._calculate_final_price(self.base_price, best_discount)
            final_price = self._convert_final_price(final_price)
            base_price: Decimal = self._convert_final_price(self.base_price)

            return {
                'final_price': final_price,
                'base_price': base_price,
                'base_discounts': base_discounts,
                'other_discounts': other_discounts,
                'current_discount': best_discount,
                'incompatible_with': incompatible_with,
                'detail': ''
            }
        except Exception as e:
            logger.exception(f'Calculate discount failed: {e}')

            final_price: Decimal = self.base_price
            final_price = self._convert_final_price(final_price)

            return {
                'final_price': final_price,
                'base_price': final_price,
                'base_discounts': [],
                'other_discounts': [],
                'current_discount': None,
                'incompatible_with': {},
                'detail': DISCOUNT_ERRORS['detail']
            }

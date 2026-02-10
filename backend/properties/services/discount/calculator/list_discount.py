from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, List, Dict

if TYPE_CHECKING:
    from properties.models import Property, Currency, DiscountProperty

import logging
from decimal import Decimal

from django.db.models import Q, QuerySet, Prefetch
from django.utils import timezone

from properties.models import Discount
from properties.services.discount.calculator.base import BaseCalculator
from properties.utils.choices.discount import DiscountType, DiscountStatus
from properties.utils.error_messages.discounts import DISCOUNT_ERRORS

logger = logging.getLogger(__name__)


class ListDiscountCalculator(BaseCalculator):
    """
    Discount calculator for bulk processing of multiple Property instances.

    This class extends `BaseCalculator` and implements logic required to:
        - Efficiently fetch all discounts applicable across a list of properties.
        - Distribute applicable discounts to each property individually.
        - Select the best discount per property based on savings, priority, and
          minimum-price rules.
        - Compute both final and base prices with optional currency conversion.
        - Attach pricing results directly onto each Property instance (via `prop.pricing`).

    Designed for use in:
        - property listing APIs,
        - search results,
        - mass price recalculation tasks.

    Attributes:
        property_list (List[Property]):
            List of properties for which prices are being calculated.
        property_ids_list (List[int]):
            Cached list of all property IDs for efficient queries.
        property_base_price_list (Dict[int, Decimal]):
            Mapping of property_id → precomputed base price including taxes/fees.
    """

    def __init__(self, property_list: QuerySet[Property], currency: Currency | None) -> None:
        super().__init__(currency)
        self.property_list = property_list
        self.property_ids_list: List[int] = [prop.pk for prop in self.property_list]
        self.property_base_price_list: Dict[int, Decimal] = self._set_base_prices()

    def _set_base_prices(self) -> Dict[int, Decimal]:
        """
        Compute and cache base prices for all properties.

        Base price includes `base_price + taxes_fees`, rounded to two decimals.

        Returns:
            Dict[int, Decimal]:
                Mapping of property_id → base price.
        """
        prices: Dict[int, Decimal] = {}

        for prop in self.property_list:
            prices[prop.pk] = self._get_base_price(prop)

        return prices

    def _request_discounts(self) -> QuerySet[Discount]:
        """
        Fetch all discounts applicable to any property in `property_list`.

        Includes discounts assigned directly to properties via DiscountProperty.

        Uses `prefetch_related` to avoid N+1 queries for:
            - discount.discount_properties

        Returns:
            QuerySet[Discount]:
                Distinct set of applicable seasonal/referral discounts.
        """
        now = timezone.now()

        return Discount.objects.filter(
            status=DiscountStatus.ACTIVE.value[0],
            type__in=[DiscountType.SEASONAL.value[0], DiscountType.REFERRAL.value[0]],
            discount_properties__property_id__in=self.property_ids_list,
            discount_properties__is_active=True
        ).filter(
            Q(valid_from__isnull=True) | Q(valid_from__lte=now),
            Q(valid_until__isnull=True) | Q(valid_until__gte=now)
        ).distinct().prefetch_related(
            Prefetch(
                'discount_properties',
                queryset=DiscountProperty.objects.filter(
                    property_id__in=self.property_ids_list,
                    is_active=True
                ),
                to_attr='linked_properties'
            )

        )

    @staticmethod
    def _discount_distribution(discounts) -> Dict[int, List[Discount]]:
        """
        Build a mapping of property_id → applicable discounts.

        Only direct property discounts (via DiscountProperty) are distributed.

        Args:
            discounts (Iterable[Discount]):
                Discounts returned by `_request_discounts()`.

        Returns:
            Dict[int, List[Discount]]:
                Mapping of property_id → list of applicable Discount objects.
        """

        property_discounts_dict: Dict[int, List[Discount]] = defaultdict(list)

        for discount in discounts:
            for discount_property in discount.linked_properties:
                property_discounts_dict[discount_property.property_id].append(discount)

        return property_discounts_dict

    def calculate(self) -> QuerySet[Property]:
        """
        Perform full discount calculation for all properties in the list.

        Workflow:
            1. Fetch all applicable discounts across property_list.
            2. If no discounts exist → assign base price for each property.
            3. Distribute discounts to each individual property.
            4. Select best discount per property using BaseCalculator logic.
            5. Compute final/base prices with currency conversion if enabled.
            6. Store results directly in property.pricing.

        Result format in each `Property`:
            prop.pricing = {
                'final_price': Decimal,
                'base_price': Decimal,
                'detail': str
            }

        Returns:
            List[Property]:
                Same list as input, but with calculated `pricing` attribute set.

        Error Handling:
            Any unexpected exception is logged, and each property receives
            fallback pricing with an error detail.
        """
        try:
            discount_list: QuerySet[Discount] = self._request_discounts()

            if not discount_list.exists():
                for prop in self.property_list:
                    price: Decimal = self._calculate_final_price(self.property_base_price_list[prop.pk])
                    prop.pricing = {
                        'final_price': price,
                        'base_price': price,
                        'detail': ''
                    }

                return self.property_list

            distributed_discounts: Dict[int, List[Discount]] = self._discount_distribution(discount_list)

            property_final_prices: Dict[int, Dict[str, Decimal]] = {}

            for key, value in distributed_discounts.items():
                base_price: Decimal = self.property_base_price_list[key]
                discount: Discount = self._set_base_discount(base_price, value)
                final_price: Decimal = self._calculate_final_price(base_price, discount)
                converted_price: Dict[str, Decimal] = {
                    'final_price': self._convert_final_price(final_price),
                    'base_price': self._convert_final_price(base_price)
                }
                property_final_prices[key] = converted_price

            for prop in self.property_list:
                prices: Dict[str, Decimal] = property_final_prices[prop.pk]

                prop.pricing = {
                    'final_price': prices['final_price'],
                    'base_price': prices['base_price'],
                    'detail': ''
                }

            return self.property_list

        except Exception as e:
            logger.exception(f'Calculate discounts list failed: {e}')

            for prop in self.property_list:
                price: Decimal = self._calculate_final_price(self.property_base_price_list[prop.pk])
                prop.pricing = {
                    'final_price': price,
                    'base_price': price,
                    'detail': DISCOUNT_ERRORS['detail']
                }

            return self.property_list

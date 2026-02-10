from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict, Any

if TYPE_CHECKING:
    from properties.models import Property, Currency

from abc import ABC, abstractmethod

from decimal import Decimal, ROUND_HALF_UP

from django.db.models import QuerySet

from properties.models import Discount
from properties.utils.choices.discount import DiscountValueType
from properties.utils.constants.property import MIN_PRICE


class BaseCalculator(ABC):
    """
    Abstract base class providing shared pricing and discount-calculation logic
    for models that require price evaluation with applied discounts. This class
    encapsulates the standard workflow for determining the effective price of a
    product (or property) based on available discounts, currency conversion, and
    minimum allowable pricing rules.

    Core Responsibilities:
        - Retrieve relevant discounts for a given model or list of models.
        - Compute the base price including taxes and fees.
        - Evaluate all applicable discounts and determine the most beneficial one.
        - Ensure the final price does not fall below the allowed minimum (MIN_PRICE).
        - Convert calculated prices into the target currency, if provided.
        - Provide reusable mechanisms for subclasses that operate on a single
          instance or a list of instances.

    Typical usage:
        Subclasses implement:
            - `_request_discounts()`
                to fetch applicable Discount queryset.
            - `calculate()`
                to compute final pricing for one instance or multiple instances.

    Attributes:
        currency (Currency):
            A Currency instance defining the target conversion rate. If omitted,
            all prices remain in the base currency.
    """

    def __init__(self, currency: Currency) -> None:
        self.currency = currency

    @staticmethod
    def _get_base_price(instance) -> Decimal:
        """
        Compute the base price of an instance by summing its base price and
        taxes/fees, and rounding the result to two decimal places.

        Args:
            instance:
                Model instance containing `base_price` and `taxes_fees`.

        Returns:
            Decimal: Rounded base price including taxes and fees.
        """
        return (instance.base_price + instance.taxes_fees).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def _set_base_discount(self, base_price: Decimal, discounts: List[Discount]) -> Discount | None:
        """
        Determine the best discount from a list of discounts based on maximum
        monetary saving and priority rules. Ensures the resulting final price
        does not drop below the allowed minimum threshold.

        Discount selection rules:
            - Choose the discount that yields the highest saving.
            - If savings are equal, choose the discount with the highest priority.
            - Skip discounts that reduce the price below MIN_PRICE % of base price.

        Args:
            base_price (Decimal):
                The price before applying any discount.
            discounts (List[Discount]):
                A list of eligible discount objects.

        Returns:
            Discount | None:
                The most beneficial discount or `None` if none are applicable.
        """
        if not discounts:
            return None

        min_allowed_price: Decimal = (base_price * (MIN_PRICE / 100)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        best_saving = Decimal('0')

        best_discount: Discount | None = None

        for discount in discounts:
            saving: Decimal = self._calculate_saving_value(base_price, discount)

            temp_final_price: Decimal = (base_price - saving).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            if temp_final_price < min_allowed_price:
                continue

            if saving > best_saving:
                best_saving = saving
                best_discount = discount
            elif saving == best_saving and best_discount:
                if discount.priority < best_discount.priority:
                    best_discount = discount

        return best_discount

    @staticmethod
    def _calculate_saving_value(base_price: Decimal, discount: Discount) -> Decimal:
        """
        Calculate the monetary saving provided by a discount.

        Supports both percentage and fixed-amount discount types.

        Args:
            base_price (Decimal): The price before discount.
            discount (Discount): A discount instance.

        Returns:
            Decimal: The amount saved due to the discount.
        """
        if discount.value_type == DiscountValueType.PERCENTAGE.value[0]:
            return base_price * (discount.value / 100)
        else:
            return discount.value

    @staticmethod
    def _calculate_final_price(base_price: Decimal, best_discount: Discount | None = None) -> Decimal:
        """
        Compute the final price after applying a discount. If no discount is
        provided, the base price is returned unchanged.

        Args:
            base_price (Decimal): Original price.
            best_discount (Discount | None): Selected discount.

        Returns:
            Decimal: Final discounted price.
        """
        if not best_discount:
            return base_price

        if best_discount.value_type == DiscountValueType.PERCENTAGE.value[0]:
            discounted_price = base_price - (base_price * (best_discount.value / Decimal('100')))
            discounted_price = discounted_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            discounted_price = (base_price - best_discount.value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return discounted_price

    def _convert_final_price(self, price: Decimal) -> Decimal:
        """
        Convert the given price to the target currency using the conversion rate
        stored in the `currency` attribute. If no currency is set, the price is
        returned unchanged.

        Args:
            price (Decimal): Price in base currency.

        Returns:
            Decimal: Converted price rounded to two decimals.
        """
        if self.currency:
            return (price * self.currency.rate_to_base).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return price

    @abstractmethod
    def _request_discounts(self) -> QuerySet[Discount]:
        """
        Retrieve all discounts relevant to the current calculation context.

        This method must be implemented by subclasses and should return a queryset
        of Discount instances already optimized using `select_related`,
        `prefetch_related`, or custom filters as needed.

        Returns:
            QuerySet[Discount]: Discounts applicable to the calculation.
        """
        pass

    @abstractmethod
    def calculate(self) -> Dict[str, Any] | List[Property]:
        """
        Execute the full calculation workflow.

        Subclasses must implement either:
            - single-instance calculation returning a dictionary with pricing data, or
            - bulk calculation returning a list of model instances with populated
              pricing fields.

        Should handle:
            - discount retrieval
            - discount filtering and selection
            - price calculation and currency conversion
            - error handling and fallback values

        Returns:
            Dict[str, Any] | List[Property]:
                Pricing result depending on subclass implementation.
        """
        pass

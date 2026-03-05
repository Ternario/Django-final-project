from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Tuple

from django.db.models import QuerySet

from properties.models import Discount, Property, DiscountProperty
from properties.services.discount.utils import DISCOUNT_APPLICATION_ORDER
from properties.utils.choices.discount import (
    DiscountValueType, DiscountType, DiscountStackPolicy, DiscountPropertyStatus
)
from properties.utils.constants.property import MIN_PRICE
from properties.utils.decorators import atomic_handel


class DiscountApplier:
    """
    Service class for applying discounts to Property instances based on
    associated DiscountProperty entries.

    This class implements logic to:
        - Fetch all relevant DiscountProperty objects for given IDs.
        - Group discounts by property.
        - Select applicable discounts according to stack policies, type, and
          incompatibility rules.
        - Apply selected discounts to compute final discounted prices.
        - Save both discounted prices and applied discounts to the database.

    Designed for use in:
        - post-creation processing of DiscountProperty entries,
        - bulk discount recalculation tasks.
    """
    _SEASONAL: str = DiscountType.SEASONAL.value[0]
    _OWNER_PROMO: str = DiscountType.OWNER_PROMO.value[0]

    _STACKABLE: str = DiscountStackPolicy.STACKABLE.value[0]
    _EXCLUSIVE: str = DiscountStackPolicy.EXCLUSIVE.value[0]
    _TYPE_EXCLUSIVE: str = DiscountStackPolicy.TYPE_EXCLUSIVE.value[0]

    @staticmethod
    def _get_updating_properties(dp_ids: List[int]) -> (QuerySet[Property], List[int]):
        """
        Fetch Property instances affected by the provided DiscountProperty IDs.

        Returns:
            Tuple[QuerySet[Property], List[int]]:
                - QuerySet of Property objects that need discount recalculation.
                - List of corresponding property IDs for efficient querying.
        """
        properties: QuerySet[Property] = Property.objects.filter(
            property_discounts__id__in=dp_ids,
        ).distinct().only('id', 'total_price', 'discounted_price')

        property_ids: List[int] = [prop.pk for prop in properties]

        return properties, property_ids

    def _discount_distribution(self, property_ids: List[int]) -> Dict[int, List[Discount]]:
        """
        Build mapping of property_id → applicable discounts.

        Only active DiscountProperty objects of type SEASONAL or OWNER_PROMO
        are considered.

        Args:
            property_ids (List[int]): List of property IDs to process.

        Returns:
            Dict[int, List[Discount]]: Mapping of property_id to list of discounts.
        """
        active_dp: List[DiscountProperty] = DiscountProperty.objects.filter(
            property_ref_id__in=property_ids,
            status=DiscountPropertyStatus.ACTIVE.value[0],
            discount__type__in=[self._SEASONAL, self._OWNER_PROMO]
        ).select_related('discount').prefetch_related('discount__incompatible_with')

        property_to_discounts: Dict[int, List[Discount]] = defaultdict(list)

        for dp in active_dp:
            property_to_discounts[dp.property_ref_id].append(dp.discount)

        return property_to_discounts

    def _select_discounts(self, discounts: List[Discount]) -> List[Discount]:
        """
        Select applicable discounts based on stack policies, type, and incompatibilities.

        Rules:
            - Exclusive discounts prevent applying any other discounts.
            - Type-exclusive discounts prevent applying multiple discounts of the same type.
            - Stackable discounts can be combined if not incompatible with others.

        Args:
            discounts (List[Discount]): List of discounts to evaluate.

        Returns:
            List[Discount]: Discounts selected to apply to the property.
        """
        if not discounts:
            return []

        selected: List[Discount] = []

        for discount_type in DISCOUNT_APPLICATION_ORDER:
            type_discounts: List[Discount] = [d for d in discounts if d.type == discount_type]

            if not type_discounts:
                continue

            for discount in type_discounts:
                if any(d.stack_policy == self._EXCLUSIVE for d in selected):
                    return selected

                if discount.stack_policy == self._EXCLUSIVE:
                    selected.append(discount)
                    break

                if discount.stack_policy == self._TYPE_EXCLUSIVE:
                    if any(
                            d.type == discount.type and d.stack_policy in [self._STACKABLE, self._TYPE_EXCLUSIVE]
                            for d in selected
                    ):
                        continue

                conflict = False

                for applied in selected:
                    if (
                            discount in applied.incompatible_with.all() or applied in discount.incompatible_with.all()
                    ):
                        conflict = True
                        break

                if conflict:
                    continue

                selected.append(discount)

        return selected

    @staticmethod
    def _apply_discounts(total_price: Decimal, discounts: List[Discount]) -> Decimal:
        """
        Compute the final price after applying selected discounts.

        Discounts are applied in order with respect to MIN_PRICE restriction.
        Each discount can reduce price but final price cannot fall below
        MIN_PRICE % of total_price.

        Args:
            total_price (Decimal): Original price of the property.
            discounts (List[Discount]): List of discounts to apply.

        Returns:
            Decimal: Discounted price after applying selected discounts.
        """
        if not discounts:
            return total_price

        price: Decimal = total_price

        min_allowed_price: Decimal = (total_price * (MIN_PRICE / 100)).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        for discount in discounts:
            if discount.value_type == DiscountValueType.PERCENTAGE.value[0]:
                discount_value = price * (discount.value / 100)
            else:
                discount_value = discount.value

            new_price = price - discount_value
            new_price = new_price.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            if new_price < min_allowed_price:
                continue

            price = new_price

        return price

    @atomic_handel
    def execute(self, dp_ids: List[int]) -> None:
        """
        Main entry point to apply discounts to affected Property instances.

        Arguments:
            dp_ids (List[int]): List of DiscountProperty IDs that trigger recalculation.

        Steps:
            - Fetch properties linked to the given DiscountProperty IDs.
            - Build mapping of properties → active discounts of type SEASONAL or OWNER_PROMO.
            - For each property, select applicable discounts according to stack policies, type, and incompatibilities.
            - Compute final discounted price for each property.
            - Collect Property instances for bulk update of `discounted_price`.
            - Prepare M2M relationships (Property ↔ Discount) for bulk update.
            - Execute bulk update of discounted prices.
            - Delete old M2M relations and bulk insert the selected discounts for each property.
        """
        properties, property_ids = self._get_updating_properties(dp_ids)

        property_to_discounts = self._discount_distribution(property_ids)

        prop_to_update: List[Property] = []
        m2m_discounts_to_update: List[Property.applied_discounts.through] = []

        update_through_model = Property.applied_discounts.through

        for prop in properties:
            discounts: List[Discount] = property_to_discounts.get(prop.pk, [])

            if not discounts:
                continue

            selected_discounts: List[Discount] = self._select_discounts(discounts)

            prop.discounted_price = self._apply_discounts(prop.total_price, selected_discounts)

            prop_to_update.append(prop)

            for discount in selected_discounts:
                m2m_discounts_to_update.append(update_through_model(property_id=prop.pk, discount_id=discount.pk))

        Property.objects.bulk_update(prop_to_update, ['discounted_price'])

        update_through_model.filter(property_id__in=[p.pk for p in prop_to_update]).delete()
        update_through_model.bulk_create(m2m_discounts_to_update, ignore_conflicts=True)

from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, List, Dict, Set, Any

if TYPE_CHECKING:
    from properties.models import User, Property

import logging

from django.db.models import Q
from django.utils import timezone

from properties.models import Discount
from properties.utils.choices.discount import (
    DiscountType, DiscountStatus, DiscountUserStatus, DiscountPropertyStatus, DiscountStackPolicy
)

logger = logging.getLogger(__name__)


class DiscountUserApplier:
    """
    Service class for fetching and validating user-specific discounts
    applicable to a given Property instance.

    This class implements logic to:
        - Retrieve all active discounts assigned to a specific user, including
          COUPON, REFERRAL, WELCOME, and COMPENSATION types.
        - Filter discounts based on validity dates (`valid_from`, `valid_until`)
          and optional expiration of user-assigned discounts.
        - Ensure that discounts are relevant to the target Property either
          via admin creation or linked DiscountProperty entries.
        - Build a compatibility map enforcing stack policies:
            * Exclusive discounts cannot be combined with any other discounts.
            * Type-exclusive discounts cannot be combined with other discounts
              of the same type.
            * Stackable discounts can be combined unless explicitly incompatible.
        - Return both the list of user discounts and constraints for validation.

    Designed for use in:
        - Pre-booking validation for user-applied discounts.
        - Ensuring business rules for user-specific discounts are enforced
          before booking creation or price calculation.
    """
    _COUPON: str = DiscountType.COUPON.value[0]
    _REFERRAL: str = DiscountType.REFERRAL.value[0]
    _WELCOME: str = DiscountType.WELCOME.value[0]
    _COMPENSATION: str = DiscountType.COMPENSATION.value[0]

    _STACKABLE: str = DiscountStackPolicy.STACKABLE.value[0]
    _EXCLUSIVE: str = DiscountStackPolicy.EXCLUSIVE.value[0]
    _TYPE_EXCLUSIVE: str = DiscountStackPolicy.TYPE_EXCLUSIVE.value[0]

    def __init__(self, user: User | None, instance: Property) -> None:
        self.user = user
        self.instance = instance

    def _request_discounts(self) -> List[Discount]:
        """
        Fetch all active discounts assigned to the user that are applicable
        to the given property.

        Filters applied:
            - Discount is active and assigned to the user with active status.
            - Discount type is one of COUPON, REFERRAL, WELCOME, COMPENSATION.
            - Optional expiration (`expires_at`) and validity dates (`valid_from`, `valid_until`) are respected.
            - Discount is either admin-created or linked to the target property via DiscountProperty.

        Returns:
            List[Discount]: List of Discount objects that the user can potentially apply.
        """
        now = timezone.now()

        if not self.user:
            return []

        return list(Discount.objects.filter(
            status=DiscountStatus.ACTIVE.value[0],
            type__in=[self._COUPON, self._REFERRAL, self._WELCOME, self._COMPENSATION],
            discount_users__user_id=self.user.pk,
            discount_users__status=DiscountUserStatus.ACTIVE.value[0],
        ).filter(
            Q(discount_users__expires_at__isnull=True) | Q(discount_users__expires_at__gte=now)
        ).filter(
            Q(valid_from__isnull=True) | Q(valid_from__lte=now),
            Q(valid_until__isnull=True) | Q(valid_until__gte=now),
        ).filter(
            Q(is_admin_created=True) |
            Q(
                discount_properties__property_ref_id=self.instance.pk,
                discount_properties__status=DiscountPropertyStatus.ACTIVE.value[0]
            )
        ).prefetch_related('incompatible_with').distinct())

    def _set_compatibility_map(self, discount_list: List[Discount],
                               applied_discounts: List[Discount]) -> Dict[str, Any]:
        """
        Build a compatibility map for discounts based on stack policies and incompatibilities.

        Steps:
            - Merge requested discounts and already applied discounts for the property.
            - Compute sets of incompatible discounts for each discount.
            - Categorize discounts into:
                * 'exclusive': cannot be combined with others.
                * 'type_exclusive': cannot be combined with same type discounts.
                * 'stackable': list of discounts incompatible with each discount.

        Args:
            discount_list (List[Discount]): List of user-specific discounts.
            applied_discounts (List[Discount]): Discounts already applied to the property.

        Returns:
            Dict[str, Any]: Constraints dictionary mapping discount PKs to incompatibilities and categories.
        """

        new_discount_list: Set[Discount] = set(discount_list)
        new_discount_list.update(applied_discounts)

        discounts_ids: Set[int] = {d.pk for d in new_discount_list}

        incompatibility_map: Dict[int, Set[int]] = {
            d.pk: {inc.pk for inc in d.incompatible_with.all() if inc.pk in discounts_ids} for d in new_discount_list
        }

        constraints: Dict[str, Any] = {
            'exclusive': set(),
            'type_exclusive': defaultdict(set),
            'stackable': defaultdict(set)
        }

        for discount in new_discount_list:
            if discount.stack_policy == self._EXCLUSIVE:
                constraints['exclusive'].add(discount.pk)

            elif discount.stack_policy == self._TYPE_EXCLUSIVE:
                constraints['type_exclusive'][discount.type].add(discount.pk)

        for discount in new_discount_list:
            constraints['stackable'][discount.pk].update(incompatibility_map[discount.pk])

        return constraints

    def execute(self) -> Dict[str, Any]:
        """
        Main entry point to retrieve user discounts and build compatibility constraints.

        Steps:
            - Request active, valid discounts for the user.
            - If no discounts are found, return empty lists/dictionaries.
            - Generate a constraints map for compatibility and stacking rules.
            - Handle any unexpected errors gracefully and log exceptions.

        Returns:
            Dict[str, Any]:
                - 'user_discounts': List of Discount objects available to the user.
                - 'constraints': Dictionary representing stacking rules and incompatibilities.
        """
        try:
            discounts: List[Discount] = self._request_discounts()

            if not discounts:
                return {
                    'user_discounts': [],
                    'constraints': {},
                }

            constraints: Dict[str, Any] = self._set_compatibility_map(
                discounts, self.instance.applied_discounts
            )

            return {
                'user_discounts': discounts,
                'constraints': constraints,
            }

        except Exception as e:
            logger.exception(f'Compatible discount failed: {e}')

            return {
                'user_discounts': [],
                'constraints': {},
            }

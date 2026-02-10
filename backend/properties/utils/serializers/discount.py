from __future__ import annotations

from typing import List, Set

from rest_framework.relations import PrimaryKeyRelatedField

from properties.models import Discount
from properties.utils.error_messages.discounts import DISCOUNT_ERRORS


# Custom classes for m2m fields

class PKDiscountList(PrimaryKeyRelatedField):
    def __init__(self, required=False):
        super().__init__(queryset=Discount.objects.all(), many=True, write_only=True, required=required)


# Custom common function


def check_m2m_conflict(add_list: List[Discount], remove_list: List[Discount],
                       field_name: str) -> str | None:
    """
    Check for conflicts in many-to-many field updates.

    Compares the primary keys of objects in add_list and remove_list.
    If there are overlapping items, returns the corresponding error message
    from DISCOUNT_ERRORS for the given field_name. Otherwise, returns None.

    Args:
        add_list (List[Discount]): List of objects to be added.
        remove_list (List[Discount]): List of objects to be removed.
        field_name (str): Name of the M2M field for error lookup.

    Returns:
        str | None: Error message if conflict exists, else None.
    """
    if not add_list or not remove_list:
        return None

    intersection: Set[Discount] = set([item.pk for item in add_list]) & set(
        [item.pk for item in remove_list])
    if intersection:
        return DISCOUNT_ERRORS[field_name]
    return None


def handle_m2m_field(instance: Discount, field_name: str, add_list: List[Discount] = None,
                     remove_list: List[Discount] = None) -> None:
    """
    Apply additions and removals to a many-to-many field of a Discount instance.

    Fetches the M2M field by name, then adds objects from add_list and removes objects
    from remove_list using the field's add() and remove() methods.

    Args:
        instance (Discount): The model instance to update.
        field_name (str): The name of the many-to-many field to modify.
        add_list (List[Discount], optional): Objects to add. Defaults to None.
        remove_list (List[Discount], optional): Objects to remove. Defaults to None.

    Returns:
        None
    """
    field = getattr(instance, field_name)

    if add_list:
        field.add(*add_list)
    if remove_list:
        field.remove(*remove_list)

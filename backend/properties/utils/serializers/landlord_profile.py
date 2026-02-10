from __future__ import annotations

from typing import List, Set, Union

from rest_framework.relations import PrimaryKeyRelatedField

from properties.models import Language, Currency, PaymentMethod, LandlordProfile
from properties.utils.error_messages.landlord_profile import LANDLORD_PROFILE_ERRORS


# Custom classes for m2m fields
class PKLanguagesList(PrimaryKeyRelatedField):
    def __init__(self, required=False):
        super().__init__(queryset=Language.objects.all(), many=True, write_only=True, required=required)


class PKCurrenciesList(PrimaryKeyRelatedField):
    def __init__(self, required=False):
        super().__init__(queryset=Currency.objects.all(), many=True, write_only=True, required=required)


class PKPaymentMethodsList(PrimaryKeyRelatedField):
    def __init__(self, required=False):
        super().__init__(queryset=PaymentMethod.objects.all(), many=True, write_only=True, required=required)


# Custom common function

models_to_check = Union[Language, Currency, PaymentMethod]


def check_m2m_conflict(add_list: List[models_to_check], remove_list: List[models_to_check],
                       field_name: str) -> str | None:
    """
    Check for conflicts in many-to-many field updates.

    Compares the primary keys of objects in add_list and remove_list.
    If there are overlapping items, returns the corresponding error message
    from LANDLORD_PROFILE_ERRORS for the given field_name. Otherwise, returns None.

    Args:
        add_list (List[models_to_check]): List of objects to be added.
        remove_list (List[models_to_check]): List of objects to be removed.
        field_name (str): Name of the M2M field for error lookup.

    Returns:
        str | None: Error message if conflict exists, else None.
    """
    if not add_list or not remove_list:
        return None

    intersection: Set[models_to_check] = set([item.pk for item in add_list]) & set(
        [item.pk for item in remove_list])
    if intersection:
        return LANDLORD_PROFILE_ERRORS[field_name]
    return None


def handle_m2m_field(instance: LandlordProfile, field_name: str, add_list: List[models_to_check] = None,
                     remove_list: List[models_to_check] = None) -> None:
    """
    Apply additions and removals to a many-to-many field of a LandlordProfile instance.

    Fetches the M2M field by name, then adds objects from add_list and removes objects
    from remove_list using the field's add() and remove() methods.

    Args:
        instance (LandlordProfile): The model instance to update.
        field_name (str): The name of the many-to-many field to modify.
        add_list (List[models_to_check], optional): Objects to add. Defaults to None.
        remove_list (List[models_to_check], optional): Objects to remove. Defaults to None.

    Returns:
        None
    """
    field = getattr(instance, field_name)

    if add_list:
        field.add(*add_list)
    if remove_list:
        field.remove(*remove_list)

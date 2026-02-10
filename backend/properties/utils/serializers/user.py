from __future__ import annotations

from typing import List, Dict, Any

from datetime import date

from rest_framework.exceptions import ValidationError

from properties.utils.constants.age import AGE

from properties.utils.error_messages.user import USER_ERRORS
from properties.utils.regex_patterns import match_user_name


# additional user's data validator

def validate_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate user input data for creating or updating a user.

    Checks the following fields:

    - first_name: Must match the allowed name pattern defined in `match_user_name`.
    - last_name: Must match the allowed name pattern defined in `match_user_name`.
    - date_of_birth: Must indicate that the user meets the minimum age requirement (`AGE`).

    If any validation fails, raises a `ValidationError` with the corresponding non-field errors.

    Returns:
        The original `data` dictionary if all validations pass.
    """
    first_name: str | None = data.get('first_name', None)
    last_name: str | None = data.get('last_name', None)

    date_of_birth: date | None = data.get('date_of_birth', None)

    non_field_errors: List[str] = []

    if first_name and not match_user_name(first_name):
        non_field_errors.append(USER_ERRORS['first_name'])

    if last_name and not match_user_name(last_name):
        non_field_errors.append(USER_ERRORS['last_name'])

    if date_of_birth:
        today: date = date.today()
        age: int = today.year - date_of_birth.year - (
                (today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        if age < AGE:
            non_field_errors.append(USER_ERRORS['date_of_birth'])

    if non_field_errors:
        raise ValidationError({'non_field_errors': non_field_errors})

    return data

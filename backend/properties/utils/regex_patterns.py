import re


def match_phone_number(phone: str) -> bool:
    return bool(re.match(r'^\+[1-9]\s*\(?\d+\)?\s*\d+(?:[-\s]*\d+)*$', phone))


def match_user_name(name: str) -> bool:
    return bool(re.match('^[a-zA-Z]+(?:-*[a-zA-Z]+)+(?:-*[a-zA-Z]+)*$', name))

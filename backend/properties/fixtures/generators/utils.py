from __future__ import annotations


from typing import Dict, Tuple

user_type: Dict[int, str] = {
    1: 'superuser',
    2: 'admin',
    3: 'regular'
}


def set_personal_data(index: int) -> Tuple[str, str]:
    password: str = f'UserPass{index:02}!-'
    phone: str = f'+100000000{index:02}'

    return password, phone


SUCCESS_LOG_INFO: str = '... OK'

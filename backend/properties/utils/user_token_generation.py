import hmac
import hashlib

from base_config import settings


def make_user_token(user_id: int, context: str = 'moderation') -> str:
    """
    Generates an anonymous token for the user using HMAC.
    :param user_id:
            Original user id.
    :param context:
            "moderation", "public_export", "internal_audit", etc.
    :return:
            Returns the generated token in string format.
    """

    key = settings.USER_TOKEN_SECRET.encode()
    data = f'{user_id}{context}'.encode()

    return hmac.new(key, data, hashlib.sha256).hexdigest()

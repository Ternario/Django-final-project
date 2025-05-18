from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken


def set_jwt_cookies(response, user):
    refresh_token = RefreshToken.for_user(user)
    refresh_token_str = str(refresh_token)
    refresh_token_exp = refresh_token['exp']
    refresh_token_exp = timezone.datetime.fromtimestamp(
        refresh_token_exp,
        tz=timezone.get_current_timezone()
    )
    access_token = refresh_token.access_token
    access_token_str = str(access_token)
    access_token_exp = access_token['exp']
    access_token_exp = timezone.datetime.fromtimestamp(
        access_token_exp,
        tz=timezone.get_current_timezone()
    )

    response.set_cookie(
        'refresh_token',
        refresh_token_str,
        expires=refresh_token_exp,
        httponly=True,
        samesite='None'
    )
    response.set_cookie(
        'access_token',
        access_token_str,
        expires=access_token_exp,
        httponly=True,
        samesite='None'
    )

    return response

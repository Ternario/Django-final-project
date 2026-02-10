from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from properties.models import User
    from django.http import HttpResponse
    from datetime import datetime

from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken


def set_jwt_cookies(response: HttpResponse, user: User) -> HttpResponse:
    """
    Set JWT access and refresh tokens as HTTP-only cookies on the response.

    This function generates a new pair of JWT tokens for the given user:
        - `refresh_token`: long-lived token used to obtain new access tokens.
        - `access_token`: short-lived token used for authentication in requests.

    The tokens are then set in the response cookies with the following properties:
        - HttpOnly: True, preventing JavaScript access.
        - SameSite: 'None', allowing cross-site requests (adjust if needed).
        - Expires: based on the token's `exp` claim.

    Args:
        response (HttpResponse): Django HTTP response object to attach cookies to.
        user (User): The user instance for whom the JWT tokens will be generated.

    Returns:
        HttpResponse: The same response object with `access_token` and `refresh_token` cookies set.

    Notes:
        - `refresh_token` and `access_token` are generated using `rest_framework_simplejwt.tokens`.
        - Expiration timestamps (`exp`) are converted to timezone-aware `datetime` objects
          using Django's current timezone.
        - This function does not return a new response; it modifies the input `response` in-place.
    """
    refresh_token: RefreshToken = RefreshToken.for_user(user)
    refresh_token_str = str(refresh_token)
    refresh_exp: int = refresh_token['exp']
    refresh_token_exp: datetime = timezone.datetime.fromtimestamp(
        refresh_exp,
        tz=timezone.get_current_timezone()
    )
    access_token = refresh_token.access_token
    access_token_str: str = str(access_token)
    access_exp: int = access_token['exp']
    access_token_exp: datetime = timezone.datetime.fromtimestamp(
        access_exp,
        tz=timezone.get_current_timezone()
    )

    response.set_cookie(
        'refresh_token',
        refresh_token_str,
        expires=refresh_token_exp,
        httponly=True,
        samesite='lax'
    )
    response.set_cookie(
        'access_token',
        access_token_str,
        expires=access_token_exp,
        httponly=True,
        samesite='lax'
    )

    return response

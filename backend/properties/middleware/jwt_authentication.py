from __future__ import annotations
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from rest_framework_simplejwt.tokens import Token
    from django.http import HttpRequest, HttpResponse

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, Token
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to handle JWT authentication via access and refresh tokens stored in cookies.

    Responsibilities:
        - Automatically attach the access token to the request header if valid.
        - Refresh expired access tokens using a refresh token.
        - Clear authentication cookies if tokens are invalid or expired.
        - Set updated access tokens in the response cookies.

    Attributes:
        None
    """

    def process_request(self, request) -> None:
        """
        Process incoming HTTP requests to authenticate users based on JWT tokens.

        Steps:
            1. Retrieve 'access_token' and 'refresh_token' from request cookies.
            2. Validate access token expiration and attach it to the Authorization header.
            3. If the access token is expired, attempt to refresh using the refresh token.
            4. Clear cookies if both tokens are invalid or expired.

        Args:
            request (HttpRequest): The incoming Django request object.

        Returns:
            None: Modifies the request object in-place by updating `META` and setting `_new_access_token`.
        """
        access_token: str | None = request.COOKIES.get('access_token')
        refresh_token: str | None = request.COOKIES.get('refresh_token')

        if access_token:
            try:
                token: AccessToken = AccessToken(cast(Token, access_token))
                if datetime.fromtimestamp(token['exp']) < datetime.now():
                    raise TokenError('Token is expired')
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            except TokenError:
                new_access_token: str | None = self.refresh_access_token(refresh_token)
                if new_access_token:
                    request.META['HTTP_AUTHORIZATION'] = f'Bearer {new_access_token}'
                    request._new_access_token = new_access_token
                else:
                    self.clear_cookies(request)
        elif refresh_token:
            new_refresh_token: str | None = self.refresh_access_token(refresh_token)
            if new_refresh_token:
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {new_refresh_token}'
                request._new_access_token = new_refresh_token
            else:
                self.clear_cookies(request)

    @staticmethod
    def refresh_access_token(refresh_token: str | None) -> str | None:
        """
        Attempt to refresh an access token using a valid refresh token.

        Args:
            refresh_token (str | None): JWT refresh token retrieved from cookies.

        Returns:
            str | None: Returns a new access token if refresh is successful, otherwise None.

        Raises:
            TokenError: If the refresh token is invalid or expired.
        """
        if not refresh_token:
            return None
        try:
            refresh: RefreshToken = RefreshToken(cast(Token, refresh_token))
            new_access_token: str = str(refresh.access_token)
            return new_access_token
        except TokenError:
            return None

    @staticmethod
    def process_response(request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Process outgoing HTTP responses to set new access tokens in cookies.

        Steps:
            1. Check if a new access token has been generated during request processing.
            2. If present, set the 'access_token' cookie with the updated token and expiration time.

        Args:
            request (HttpRequest): The request object, possibly containing `_new_access_token`.
            response (HttpResponse): The response object to attach the cookie to.

        Returns:
            HttpResponse: The response object with updated cookies if applicable.
        """
        new_access_token: str | None = getattr(request, '_new_access_token', None)
        if new_access_token:
            access_expiry: AccessToken = AccessToken(cast(Token, new_access_token))['exp']
            response.set_cookie(
                'access_token',
                new_access_token,
                expires=access_expiry,
                httponly=True
            )
        return response

    def clear_cookies(self, request: HttpRequest) -> None:
        """
        Clear authentication cookies from the request to force logout.

        Args:
            request (HttpRequest): The request object containing cookies.

        Returns:
            None: Removes 'access_token' and 'refresh_token' from `request.COOKIES`.
        """
        request.COOKIES.pop('access_token', None)
        request.COOKIES.pop('refresh_token', None)

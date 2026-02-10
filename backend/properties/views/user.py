from __future__ import annotations
from typing import TYPE_CHECKING

from drf_spectacular.utils import extend_schema

if TYPE_CHECKING:
    from django.db.models import QuerySet

from django.utils.timezone import now
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from properties.permissions import IsOwnerUser
from properties.models import User
from properties.serializers import (
    UserCreateSerializer, UserSerializer, UserLandlordCreateSerializer, UserLoginSerializer
)
from properties.managers.cookies import set_jwt_cookies


class UserCAV(CreateAPIView):
    """
    API view for creating a new user account.

    - POST: create a new `User` using `UserCreateSerializer`.
    - No authentication is required (`AllowAny`), suitable for registration endpoints.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = UserCreateSerializer


class UserLandlordCAV(CreateAPIView):
    """
    API view for creating a new landlord user account.

    - POST: create a new `User` with landlord-specific fields using
      `UserLandlordCreateSerializer`.
    - No authentication is required (`AllowAny`), suitable for landlord registration.
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = UserLandlordCreateSerializer


class UserRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    """
    API view for retrieving, updating, or deleting the authenticated user's account.

    - GET: retrieve the user details, including related `language` and `currency`
      if the request method is safe (GET, HEAD, OPTIONS).
    - PUT/PATCH: update the user's account using `UserSerializer`.
    - DELETE: soft delete the user account and remove authentication cookies.
    - Permissions: only the owner of the account (`IsOwnerUser`) can access these endpoints.

    This view ensures that users can manage only their own account.
    """
    permission_classes = [IsOwnerUser]
    queryset = User.objects.not_deleted()
    serializer_class = UserSerializer

    def get_object(self) -> User:
        queryset: QuerySet = self.get_queryset()

        if self.request.method in SAFE_METHODS:
            queryset = queryset.select_related('language', 'currency')

        user: User = get_object_or_404(queryset, id=self.request.user.pk)
        self.check_object_permissions(self.request, user)

        return user

    def destroy(self, request, *args, **kwargs) -> Response:
        user = self.get_object()
        user.soft_delete()

        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response


class UserLoginView(APIView):
    """
    API view for user authentication and JWT login.

    - POST: authenticate a user using email and password.
      Returns serialized user data and sets JWT cookies on successful login.
    - No authentication is required (`AllowAny`).
    """
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer: UserLoginSerializer = self.serializer_class(
            data=self.request.data, context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        user: User = serializer.validated_data['user']

        user.last_login = now()
        user.save(update_fields=['last_login'])

        user_detail: User = UserSerializer(user).data

        response = Response(user_detail, status=status.HTTP_200_OK)
        response = set_jwt_cookies(response, user)

        return response

@extend_schema(
    request=None,
    responses={204: None},
    description="Logout user and invalidate tokens"
)
class LogoutUserView(APIView):
    """
    API view for logging out the authenticated user.

    - POST: deletes JWT cookies (`access_token` and `refresh_token`)
      to log out the user.
    - Authentication: requires the user to be authenticated (`IsAuthenticated`).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs) -> Response:
        response = Response({'detail': 'Logged out successfully.'}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

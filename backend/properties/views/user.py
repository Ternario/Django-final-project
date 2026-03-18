from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from django.db.models import QuerySet

from drf_spectacular.utils import extend_schema

from django.utils.timezone import now
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView, get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView

from properties.permissions import IsOwnerUser
from properties.models import User
from properties.serializers import (
    UserCreateSerializer, UserSerializer, UserLandlordCreateSerializer, UserLoginSerializer,
    UserLandlordActivateSerializer, UserLandlordDeactivateSerializer
)
from properties.managers.cookies import set_jwt_cookies
from properties.tasks.cascade_delete import user_soft_cascade_delete_task
from properties.utils.choices.landlord_profile import LandlordType


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
        user: User = self.get_object()

        user_soft_cascade_delete_task.delay(user.pk)

        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response


@extend_schema(
    request=UserLandlordActivateSerializer,
    responses={200: None},
    description='Return landlord type choices / activate/change landlord profile / type.'
)
class UserLandlordActivateUAV(APIView):
    """
    API view for activating a landlord profile for the authenticated user
    and retrieving available landlord types.

    - GET: return the list of available landlord types (`INDIVIDUAL`, `COMPANY`)
      for selection during activation.
    - PATCH: activate the authenticated user as a landlord and set the
      selected `landlord_type` using `UserLandlordActivateSerializer`.
    - Permissions: authentication is required (`IsAuthenticated`).

    This view handles landlord activation flow, including type selection
    and validation of business rules before activation.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs) -> Response:
        i_key, i_label = LandlordType.INDIVIDUAL
        c_key, c_label = LandlordType.COMPANY

        landlord_type: List[Dict[str, str]] = [{'key': i_key, 'label': i_label}, {'key': c_key, 'label': c_label}]
        return Response({'landlord_type': landlord_type}, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs) -> Response:
        user: User = request.user

        serializer: UserLandlordActivateSerializer = UserLandlordActivateSerializer(
            user, data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    request=UserLandlordDeactivateSerializer,
    responses={200: None},
    description='Set landlord user to regular user.'
)
class UserLandlordDeactivateUAV(APIView):
    """
    API view for deactivating the landlord status of the authenticated user.

    - POST: deactivate the user's landlord status using
      `UserLandlordDeactivateSerializer`.
    - Permissions: authentication is required (`IsAuthenticated`).

    This view performs business validation (e.g., active landlord profiles
    or company memberships) before allowing deactivation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs) -> Response:
        user: User = request.user

        serializer: UserLandlordDeactivateSerializer = UserLandlordDeactivateSerializer(instance=user, data={})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserLoginView(APIView):
    """
    API view for user authentication and JWT login.

    - POST: authenticate a user using email and password.
      Returns serialized user data and sets JWT cookies on successful login.
    - No authentication is required (`AllowAny`).
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer: UserLoginSerializer = self.serializer_class(
            data=request.data, context={'request': request}
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
    description='Logout user and invalidate tokens'
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

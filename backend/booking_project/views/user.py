from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView, get_object_or_404, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from booking_project.permissions import IsOwnerUser
from booking_project.models.user import User
from booking_project.serializers.user import UserRegisterSerializer, UserDetailSerializer, UserBaseDetailSerializer

from booking_project.utils.cookies_manager import set_jwt_cookies


class UserCreateView(CreateAPIView):
    """
    View for registration a user.

    Example of POST request:
    POST /auth/
    {
        "email": "newuser@example.com",
        "first_name": "newuser",
        "last_name": "newuser",
        "username": "newuser",
        "phone": "+1112223344",
        "password": "newuserpassword",
        "re_password": "newuserpassword"
    }

    Response:
    {
       "detail": "User successfully created."
    }

    Permissions:
         - AllowAny: This view is accessible without any authentication.
    """

    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)

        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response({"detail": "User successfully created."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserBaseDetailsRetrieveView(RetrieveAPIView):
    """
    View for retrieving basic info about user account.

    Example of GET request:
    GET /user/base/
    Response:
    {
        "id": "1",
        "email": "newuser@example.com",
        "first_name": "newuser",
        "last_name": "newuser",
        "username": "newuser",
    }

    Permissions:
        - The user must be authenticated.

    NOTE:
        - Each user has access only to his own account
    """

    permission_classes = [IsOwnerUser, IsAuthenticated]
    serializer_class = UserBaseDetailSerializer

    def get_object(self):
        user = get_object_or_404(User, email=self.request.user)
        self.check_object_permissions(self.request, user)
        return user


class UserRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, or deleting a user.

    Example of GET request:
    GET /user/
    Response:
    {
        "id": "1",
        "email": "user@example.com",
        "first_name": "user",
        "last_name": "user",
        "username": "user",
        "phone": "+123456789",
        "date_of_birth": "01.02.2025",
        "is_landlord": True (default = False)
    }

    Example of PUT request to update a user:
    PUT /user/
    {
        "email": "user@example.com",
        "first_name": "updateduser",
        "last_name": "updateduser",
        "username": "updateduser",
        "phone": "+123456789",
        "date_of_birth": "01-02-2020",
        "is_landlord": True (default = False)

    }

    Response:
    {
        "id": "1",
        "email": "user@example.com",
        "first_name": "updateduser",
        "last_name": "updateduser",
        "username": "updateduser",
        "phone": "+123456789",
        "date_of_birth": "01-02-2020",
        "is_landlord": True,
        "date_joined": join date
    }

    Example of PATCH request to partially update a user:
    PATCH /user/
    {
        "first_name": "partiallyupdateduser",  # Optional field update
    }

    Response:
    {
        "id": "1",
        "email": "user@example.com",
        "first_name": "partiallyupdateduser",
        "last_name": "updateduser",
        "username": "updateduser",
        "phone": "+123456789",
        "date_of_birth": "01-02-2020",
        "is_landlord": True,
        "date_joined": join date
    }

    Example of DELETE request:
    DELETE /user/
    Response: 204 No Content

    Permissions:
        - The user must be authenticated.

    NOTE:
     - Each user has access only to his own account
    """

    permission_classes = [IsOwnerUser, IsAuthenticated]
    serializer_class = UserDetailSerializer

    def get_object(self):
        user = get_object_or_404(User, email=self.request.user)
        self.check_object_permissions(self.request, user)
        return user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()

        response = Response({
            "detail": "User was deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class UserLoginView(CreateAPIView):
    """
    View for authenticating a user and returning JWT tokens as cookies.

    Example of POST request:
    POST /auth/login/
    {
        "email": "user@example.com",
        "password": "user password"
    }

    On successful authentication, this view sets JWT access and refresh tokens
    as cookies in the response.

    Permissions:
        - AllowAny: This view is accessible without any authentication.

    Response on success:
    - Status: 200 OK
    - Cookies: JWT access and refresh tokens

    Response on failure:
    - Status: 401 Unauthorized
    - Body: {"detail": "Invalid credentials"}
    """

    permission_classes = [AllowAny]
    serializer_class = UserBaseDetailSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = get_object_or_404(User, email=email)

        user_data = authenticate(request, username=email, password=password)

        if user_data:
            serializer = self.serializer_class(user_data)
            response = Response(serializer.data, status=status.HTTP_200_OK)
            response = set_jwt_cookies(response, user)
            return response

        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutUserView(APIView):
    """
    View for logging out the currently authenticated user.

    This view logs out the user and deletes the JWT access and refresh tokens
    from the cookies.

    Example of POST request:
    POST /auth/Logout/
    {
        No request body required
    }

    Permissions:
        - The user must be authenticated.

    Response on success:
    - Status: 200 OK
    - Cookies: JWT access and refresh tokens are deleted

    Note:
    - If no user is authenticated, the view still returns a 200 OK status,
    but no actions are performed.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

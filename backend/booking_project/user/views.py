from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView, RetrieveUpdateAPIView, \
    get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from booking_project.permissions import *
from booking_project.user.serialezers.user_serializer import *

from booking_project.utils.cookies_manager import set_jwt_cookies


class UserCreateView(CreateAPIView):
    permission_classes = (AllowAny,)
    authentication_classes = []
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer


class UserLoginView(CreateAPIView):
    permission_classes = (AllowAny,)
    authentication_classes = []
    serializer_class = UserBaseDetailSerializer

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)

        if user:
            user_data = User.objects.get(email=user)
            serializer = self.serializer_class(user_data)
            response = Response(serializer.data, status=status.HTTP_200_OK)
            response = set_jwt_cookies(response, user)
            return response

        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class UserDetailsUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsOwnerUser, IsAuthenticated)
    serializer_class = UserDetailSerializer

    def get_object(self):
        user = get_object_or_404(User, email=self.request.user)
        self.check_object_permissions(self.request, user)
        return user

    def destroy(self, request, *args, **kwargs):
        user = User.objects.get(email=request.user)
        user.delete()

        response = Response({
            "detail": "User was deleted successfully"
        }, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class LogoutUserView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from booking_project.permissions import *
from ..serialezers.user_serializer import *

from ..set_cookie import set_jwt_cookies


class UserCreateView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            response = Response({'id': user.id}, status=status.HTTP_201_CREATED)
            response = set_jwt_cookies(response, user)
            return response
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST, )


class UserLoginView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, username=email, password=password)

        if user:
            response = Response(status=status.HTTP_200_OK)
            response = set_jwt_cookies(response, user)
            return response
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class UserDetailsUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsOwnerUser, IsAuthenticated)
    serializer_class = UserDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        user = User.objects.get(email=request.user)
        user.delete()

        response = Response({
            "message": "User was deleted successfully"
        }, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response


class UserBaseDetailUserView(APIView):
    permission_classes = (IsOwnerUser, IsAuthenticated)

    def post(self, request):
        user = User.objects.get(email=request.user)

        if user:
            serializer = UserBaseDetailSerializer(user)
            response = Response(serializer.data, status=status.HTTP_200_OK)
            return response
        else:
            return Response({"detail": "User not found"}, status=status.HTTP_204_NO_CONTENT)


class LogoutUserView(APIView):
    def post(self, request, *args, **kwargs):
        response = Response(status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

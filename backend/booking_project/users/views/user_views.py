from datetime import datetime, timedelta

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User
from ..serialezers.user_serializer import *
from ..permissions import *


def set_jwt_cookies(response, user):
    # # print('get_users_token user, response: ', user, response)
    # # Создаем JWT токены
    # refresh = RefreshToken.for_user(user)
    # access_token = str(refresh.access_token)
    # refresh_token = str(refresh)
    #
    # # Убедитесь, что флаг secure установлен в True,
    # # если ваше приложение работает через HTTPS.
    # # Если вы тестируете локально без HTTPS, установите secure=False.
    # # Добавляем токены в cookies
    # response.set_cookie(
    #     'access_token', access_token,
    #     httponly=True,
    #     # httponly=True,
    #     secure=True,  # Убедитесь, что это True на продакшене
    #     samesite='lax',
    #     max_age=timedelta(minutes=25)  # Срок жизни access-токена
    # )
    # response.set_cookie(
    #     'refresh_token', refresh_token,
    #     httponly=True,
    #     secure=True,
    #     samesite='lax',
    #     # samesite='Lax',
    #     max_age=timedelta(days=7)  # Срок жизни refresh-токена
    # )
    #
    # # print('get_users_token after add setCookies, response: ', response.data)
    # return response

    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    refresh_token = refresh

    access_expiry = datetime.utcfromtimestamp(access_token['exp'])
    refresh_expiry = datetime.utcfromtimestamp(refresh['exp'])

    response.set_cookie(
        key='access_token',
        value=str(access_token),
        httponly=True,
        secure=False,
        samesite='None',
        expires=access_expiry
    )
    response.set_cookie(
        key='refresh_token',
        value=str(refresh_token),
        httponly=True,
        secure=False,
        samesite='None',
        expires=refresh_expiry
    )


class CreateUserView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            response = Response({'id': user.id}, status=status.HTTP_201_CREATED)
            set_jwt_cookies(response, user)
            return response
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST, )


class LoginUserView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)

        if user:
            user_data = User.objects.get(email=email)
            serializer = UserBaseDetailSerializer(user_data)
            response = Response(serializer.data, status=status.HTTP_200_OK)
            set_jwt_cookies(response, user)
            return response
        else:
            return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class DetailUserView(APIView):
    permission_classes = (IsOwner, IsAuthenticated)

    def post(self, request):
        user = User.objects.get(email=request.user)

        if user:
            serializer = UserDetailSerializer(user)
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


class DeleteUserView(APIView):
    permission_classes = (IsOwner, IsAuthenticated)

    def delete(self, request):
        user = User.objects.get(email=request.user)
        user.delete()

        response = Response({
            "message": "User was deleted successfully"
        }, status=status.HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response

        # return Response(
        #         {
        #             "message": "User was deleted successfully"
        #         },
        #         status=status.HTTP_200_OK,
        #     )

        # if serializer.is_valid(raise_exception=True):
        #     user.delete()
        #
        #     return Response(
        #         data={
        #             "message": "User was deleted successfully"
        #         },
        #         status=status.HTTP_200_OK,
        #     )
        #
        # else:
        #     return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

        # email = request.data.get('email')
        # password = request.data.get('password')
        # user = User.objects.get(email=email)
        # serializer = UserDeleteSerializer(user)
        # serializer.save()
        # return Response(serializer.data)

        # if user:
        #     if user.check_password(password):
        #         user.delete()
        #
        #         response = Response({"details": "Successfully deleted"}, status=status.HTTP_200_OK)
        #         response.delete_cookie('access_token')
        #         response.delete_cookie('refresh_token')
        #         return response
        #     else:
        #         return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        # else:
        #     return Response({"detail": "User not found"}, status=status.HTTP_204_NO_CONTENT)

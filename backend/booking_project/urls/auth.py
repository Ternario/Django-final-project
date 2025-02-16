from django.urls import path

from booking_project.views.user import UserCreateView, UserLoginView, LogoutUserView

urlpatterns = [
    path('', UserCreateView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', LogoutUserView.as_view(), name="user-logout"),
]

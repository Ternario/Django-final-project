from django.urls import path

from .views.user_views import *

urlpatterns = [
    path('registration/', CreateUserView.as_view(), name='user-registration'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('logout/', LogoutView.as_view(), name="user-logout")
]
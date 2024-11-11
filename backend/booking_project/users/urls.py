from django.urls import path

from .views.user_views import *

urlpatterns = [
    path('registration/', CreateUserView.as_view(), name='user-registration'),
    path('login/', LoginUserView.as_view(), name='user-login'),
    path('logout/', LogoutUserView.as_view(), name="user-logout"),
    path('details/', DetailUserView.as_view(), name="user-detail"),
    path('delete/', DeleteUserView.as_view(), name='user-delete'),
]

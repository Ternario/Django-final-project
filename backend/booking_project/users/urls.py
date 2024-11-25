from django.urls import path

from .views.user_views import *

urlpatterns = [
    path('registration/', UserCreateView.as_view(), name='user-registration'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', LogoutUserView.as_view(), name="user-logout"),
    path('details/', UserDetailsUpdateDeleteView.as_view(), name="user-detail"),
    path('details/image/', UserImageUpdate.as_view(), name='user-details-image'),
]

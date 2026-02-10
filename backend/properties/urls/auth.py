from django.urls import path

from properties.views.user import UserCAV, UserLoginView, LogoutUserView, UserLandlordCAV

urlpatterns = [
    path('create/', UserCAV.as_view(), name='user-create'),
    path('create-landlord/', UserLandlordCAV().as_view(), name='user-landlord-create'),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('logout/', LogoutUserView.as_view(), name='user-logout'),
]

from django.urls import path

from booking.views.user import UserRetrieveUpdateDeleteView, UserBaseDetailsRetrieveView

urlpatterns = [
    path('', UserRetrieveUpdateDeleteView.as_view(), name="user-details"),
    path('base/', UserBaseDetailsRetrieveView.as_view(), name="user-base-details")
]

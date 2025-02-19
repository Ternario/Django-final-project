from django.urls import path

from booking_project.views.user import UserDetailsUpdateDeleteView, UserBaseDetailsRetrieveView

urlpatterns = [
    path('', UserDetailsUpdateDeleteView.as_view(), name="user-details"),
    path('base/', UserBaseDetailsRetrieveView.as_view(), name="user-base-details")
]

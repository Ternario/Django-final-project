from django.urls import path

from booking_project.user.views import UserDetailsUpdateDeleteView

urlpatterns = [
    path('details/', UserDetailsUpdateDeleteView.as_view(), name="user-detail")
]

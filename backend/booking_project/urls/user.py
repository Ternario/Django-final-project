from django.urls import path

from booking_project.views.user import UserDetailsUpdateDeleteView

urlpatterns = [
    path('', UserDetailsUpdateDeleteView.as_view(), name="user-detail")
]

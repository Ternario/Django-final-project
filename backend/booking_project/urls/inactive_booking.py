from django.urls import path

from booking_project.views.booking import InactiveBookingDetailsUserCreate, InactiveBookingDetailsOwnerCreate

urlpatterns = [
    path('user/inactive/', InactiveBookingDetailsUserCreate.as_view(), name="booking-user-inactive"),
    path('owner/inactive/', InactiveBookingDetailsOwnerCreate.as_view(), name="booking-owner-inactive"),
]

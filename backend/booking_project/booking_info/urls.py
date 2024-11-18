from django.urls import path

from booking_project.booking_info.views.booking_view import *

urlpatterns = [
    path('owner/', BookingDetailsOwnerList.as_view(), name='booking-create'),
    path('user/', BookingDetailsUserListCreate.as_view(), name='booking-create'),
    path('user/inactive/', InactiveBookingDetailsUserCreate.as_view(), name="booking-user-inactive"),
    path('owner/inactive/', InactiveBookingDetailsOwnerCreate.as_view(), name="booking-owner-inactive"),
    path('update_owner/<int:pk>/', BookingDetailsOwnerUpdateView.as_view(), name='booking-update'),
    path('update_user/<int:pk>/', BookingDetailsUserUpdateView.as_view(), name='booking-update'),
]

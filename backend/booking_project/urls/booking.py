from django.urls import path

from booking_project.views.booking import (
    BookingDetailsOwnerList, BookingDetailsUserListCreate,
    BookingDetailsOwnerUpdateView, BookingDetailsUserUpdateView
)

urlpatterns = [
    path('owner/', BookingDetailsOwnerList.as_view(), name='booking-create'),
    path('user/', BookingDetailsUserListCreate.as_view(), name='booking-create'),
    path('owner/<int:pk>/', BookingDetailsOwnerUpdateView.as_view(), name='owner-booking-update'),
    path('user/<int:pk>/', BookingDetailsUserUpdateView.as_view(), name='user-booking-update'),
]

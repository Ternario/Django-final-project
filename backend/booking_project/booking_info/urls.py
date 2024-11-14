from django.urls import path

from booking_project.booking_info.views.booking_view import BookingDetailsOwnerUpdateView, BookingDetailsUserUpdateView, BookingDetailsListCreate

urlpatterns = [
    path('', BookingDetailsListCreate.as_view(), name='booking-create'),
    path('update_owner/', BookingDetailsOwnerUpdateView.as_view(), name='booking-update'),
    path('update_user/', BookingDetailsUserUpdateView.as_view(), name='booking-update'),
]

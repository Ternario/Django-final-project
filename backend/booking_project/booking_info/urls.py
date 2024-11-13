from django.urls import path

from booking_project.booking_info.views.booking_view import BookingDatesListCreate

urlpatterns = [
    path('create/', BookingDatesListCreate.as_view(), name='bookings_info-create')
]

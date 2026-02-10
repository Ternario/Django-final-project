from django.urls import path

from properties.views.booking import BookingTimeChoicesAV

urlpatterns = [
    path('times/', BookingTimeChoicesAV.as_view(), name='booking-time-choices')
]

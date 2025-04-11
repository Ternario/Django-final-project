from django.urls import path

from booking_project.views.booking import (
    BookingCreateView, BookingTimeChoicesRetrieveView, BookingPlacementOwnerListView, BookingOwnerListView,
    BookingPlacementOwnerRetrieveUpdateView, BookingOwnerRetrieveUpdateView, InactiveBookingPlacementOwnerListView,
    InactiveBookingOwnerListView
)

urlpatterns = [
    path('', BookingCreateView.as_view(), name='booking-create'),
    path('choices/', BookingTimeChoicesRetrieveView.as_view(), name='booking-time-choices'),
    path('owner/', BookingPlacementOwnerListView.as_view(), name='booking-placement-owner-list'),
    path('user/', BookingOwnerListView.as_view(), name='booking-owner-list'),
    path('owner/<int:pk>/', BookingPlacementOwnerRetrieveUpdateView.as_view(), name='booking-placement-owner-update'),
    path('user/<int:pk>/', BookingOwnerRetrieveUpdateView.as_view(), name='booking-owner-update'),
    path('owner/inactive/', InactiveBookingPlacementOwnerListView.as_view(), name="booking-placement-owner-inactive"),
    path('user/inactive/', InactiveBookingOwnerListView.as_view(), name="booking-owner-inactive"),

]

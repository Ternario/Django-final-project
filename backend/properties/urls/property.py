from django.urls import path

from properties.views.booking import BookingAV
from properties.views.property import PropertyPublicLAV, PropertyPublicRAV
from properties.views.review import ReviewPublicLAV

urlpatterns = [
    path('', PropertyPublicLAV.as_view(), name='property-list'),
    path('<p_lookup>/', PropertyPublicRAV.as_view(), name='property-retrieve'),
    path('<int:p_id>/reviews/', ReviewPublicLAV.as_view(), name='property-review-list'),
    path('<int:p_id>/booking/create/', BookingAV.as_view(), name='property-booking-create')
]

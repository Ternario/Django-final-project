from django.urls import path

from properties.views.booking import BookingCAV, BookingTimeChoicesAV
from properties.views.property import PropertyPublicLAV, PropertyPublicRAV
from properties.views.review import ReviewPublicLAV

urlpatterns = [
    path('', PropertyPublicLAV.as_view(), name='property-list'),
    path('<int:p_id>/', PropertyPublicRAV.as_view(), name='property-retrieve'),
    path('<int:p_id>/reviews/', ReviewPublicLAV.as_view(), name='property-review-list'),
    path('<int:p_id>/booking/', BookingTimeChoicesAV.as_view(), name='property-booking-retrieve'),
    path('<int:p_id>/booking/create/', BookingCAV.as_view(), name='property-booking-create')

]

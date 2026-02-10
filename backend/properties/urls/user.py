from django.urls import path

from properties.views.booking import BookingLAV, BookingRUAV
from properties.views.discount import DiscountUserLAV, DiscountUserRAV
from properties.views.review import ReviewCAV, ReviewAuthorLAV, ReviewRUDAV
from properties.views.user import UserRetrieveUpdateDeleteView
from properties.views.user_profile import UserProfileRUAV

urlpatterns = [
    path('', UserRetrieveUpdateDeleteView.as_view(), name='user-detail-rud'),
    path('profile/', UserProfileRUAV.as_view(), name='user-profile-rud'),

    path('reviews/', ReviewAuthorLAV.as_view(), name='user-review-list'),
    path('reviews/<int:r_id>/', ReviewRUDAV.as_view(), name='user-review-rud'),

    path('discounts/', DiscountUserLAV.as_view(), name='user-discount-list'),
    path('discounts/<int:d_id>/', DiscountUserRAV.as_view(), name='user-discount-retrieve'),

    path('bookings/', BookingLAV.as_view(), name='user-booking-list'),
    path('bookings/<int:b_id>/', BookingRUAV.as_view(), name='user-booking-list'),
    path('bookings/<int:b_id>/review/', ReviewCAV.as_view(), name='user-booking-review-create'),

]

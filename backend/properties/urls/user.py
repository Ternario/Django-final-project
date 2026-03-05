from django.urls import path

from properties.views.booking import BookingLAV, BookingRUAV
from properties.views.discount import DiscountUserLAV, DiscountUserRAV
from properties.views.review import ReviewCAV, ReviewAuthorLAV, ReviewRUDAV
from properties.views.user import UserRetrieveUpdateDeleteView, UserLandlordActivateUAV, UserLandlordDeactivateUAV
from properties.views.user_profile import UserProfileRUAV, UserProfileHandelFavoritesAV, UserPropertyFavoritesListAV

urlpatterns = [
    path('', UserRetrieveUpdateDeleteView.as_view(), name='user-detail-rud'),
    path('profile/', UserProfileRUAV.as_view(), name='user-profile-rud'),
    path('profile/favorites/', UserPropertyFavoritesListAV.as_view(), name='user-pа-list'),
    path('profile/favorites/handel/<int:p_id>/', UserProfileHandelFavoritesAV.as_view(), name='user-pf-pd'),

    path('activation/', UserLandlordActivateUAV.as_view(), name='user-la-ru'),
    path('deactivation/', UserLandlordDeactivateUAV.as_view(), name='user-ld-post'),

    path('reviews/', ReviewAuthorLAV.as_view(), name='user-review-list'),
    path('reviews/<int:r_id>/', ReviewRUDAV.as_view(), name='user-review-rud'),

    path('discounts/', DiscountUserLAV.as_view(), name='user-discount-list'),
    path('discounts/<int:d_id>/', DiscountUserRAV.as_view(), name='user-discount-retrieve'),

    path('bookings/', BookingLAV.as_view(), name='user-booking-list'),
    path('bookings/<int:b_id>/', BookingRUAV.as_view(), name='user-booking-list'),
    path('bookings/<int:b_id>/review/', ReviewCAV.as_view(), name='user-booking-review-create'),
]

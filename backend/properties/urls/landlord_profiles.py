from django.urls import path, include

from properties.views.booking import BookingPropertyOwnerLAV, BookingPropertyOwnerRUAV
from properties.views.discount import (
    DiscountCAV, DiscountLAV, DiscountRUDAV, DiscountPropertyCAV, DiscountPropertyLAV, DiscountPropertyRUV,
    DiscountUserCAV, DiscountUserPropertyOwnerLAV, DiscountUserPropertyOwnerRUAV
)
from properties.views.landlord_profiles import (
    LandlordProfileLAV, LandlordProfileAV, LandlordProfileRUDAV, LandlordProfilePublicRAV, CompanyMembershipCAV,
    CompanyMembershipLAV, CompanyMembershipRUDAV,
)
from properties.views.location import LocationCAV, LocationRUAV

from properties.views.property import PropertyCAV, PropertyOwnerLAV, PropertyOwnerRUDV, PropertyOwnerPublicLAV
from properties.views.property_detail import PropertyDetailCAV, PropertyDetailRUAV
from properties.views.property_image import PropertyImageLCAV, PropertyImageDestroyAV
from properties.views.review import ReviewPublicLAV, ReviewPropertyOwnerRUAV

urlpatterns = [
    path('create/', LandlordProfileAV.as_view(), name='host-retrieve-create'),
    path('public/<str:hash_id>/', include([
        path('', LandlordProfilePublicRAV.as_view(), name='host-public-retrieve'),
        path('properties/', PropertyOwnerPublicLAV.as_view(), name='host-pp-list')
    ])),

    path('', LandlordProfileLAV.as_view(), name='host-list'),
    path('<str:hash_id>/', include([
        path('', LandlordProfileRUDAV.as_view(), name='host-rud'),

        path('staff/create/', CompanyMembershipCAV.as_view(), name='host-cm-create'),
        path('staff/', CompanyMembershipLAV.as_view(), name='host-cm-list'),
        path('staff/<int:cm_id>/', CompanyMembershipRUDAV.as_view(), name='host-cm-rud'),

        path('discounts/create/', DiscountCAV.as_view(), name='host-discount-create'),
        path('discounts/', DiscountLAV.as_view(), name='host-discount-list'),
        path('discounts/<int:d_id>/', DiscountRUDAV.as_view(), name='host-discount-rud'),

        path('discounts/<int:d_id>/properties/create/', DiscountPropertyCAV.as_view(), name='host-dp-create'),
        path('discounts/properties/', DiscountPropertyLAV.as_view(), name='host-dp-list'),
        path('discounts/properties/<int:dp_id>/', DiscountPropertyRUV.as_view(), name='host-dp-rud'),

        path('discounts/<int:d_id>/users/create', DiscountUserCAV.as_view(), name='host-du-create'),
        path('discounts/users/', DiscountUserPropertyOwnerLAV.as_view(), name='host-du-list'),
        path('discounts/users/<int:du_id>', DiscountUserPropertyOwnerRUAV.as_view(), name='host-du-ru'),

        path('properties/create/', PropertyCAV.as_view(), name='host-property-create'),
        path('properties/', PropertyOwnerLAV.as_view(), name='host-property-list'),
        path('properties/<int:p_id>/', PropertyOwnerRUDV.as_view(), name='host-property-rud'),

        path('properties/<int:p_id>/details/create/', PropertyDetailCAV.as_view(), name='host-pd-create'),
        path('properties/<int:p_id>/details/', PropertyDetailRUAV.as_view(), name='host-pd-rud'),

        path('properties/<int:p_id>/location/create/', LocationCAV.as_view(), name='host-pl-create'),
        path('properties/<int:p_id>/location/', LocationRUAV.as_view(), name='host-pl-ru'),

        path('properties/<int:p_id>/images/', PropertyImageLCAV.as_view(), name='host-pi-lc'),
        path('properties/<int:p_id>/images/delete/', PropertyImageDestroyAV.as_view(), name='host-pi-destroy'),

        path('properties/<int:p_id>/reviews/', ReviewPublicLAV.as_view(), name='host-pr-list'),
        path('properties/<int:p_id>/reviews/<int:r_id>/', ReviewPropertyOwnerRUAV.as_view(), name='host-pr-ru'),

        path('bookings/', BookingPropertyOwnerLAV.as_view(), name='host-booking-list'),
        path('bookings/<int:id>/', BookingPropertyOwnerRUAV.as_view(), name='host-booking-rud'),

    ]))
]

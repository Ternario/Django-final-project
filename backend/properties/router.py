from django.urls import path, include

from properties.views.filters import PropertyFiltersAV

urlpatterns = [

    path('filters/', PropertyFiltersAV.as_view(), name='filters-list'),
    path('auth/', include('properties.urls.auth')),
    path('cancellation_policies/', include('properties.urls.cancellation_policy')),
    path('currencies/', include('properties.urls.currency')),
    path('discounts/', include('properties.urls.discounts')),
    path('host/', include('properties.urls.landlord_profiles')),
    path('languages/', include('properties.urls.language')),
    path('location_types/', include('properties.urls.location_types')),
    path('payment_methods/', include('properties.urls.payment_method')),
    path('payment_types/', include('properties.urls.payment_type')),
    path('properties/', include('properties.urls.property')),
    path('user/', include('properties.urls.user')),
]

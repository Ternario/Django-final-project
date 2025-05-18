from django.urls import path, include

urlpatterns = [
    path('auth/', include('booking.urls.auth')),
    path('user/', include('booking.urls.user')),
    path('categories/', include('booking.urls.category')),
    path('placement/', include('booking.urls.placement')),
    path('booking/', include('booking.urls.booking')),
    path('review/', include('booking.urls.reviews')),
]

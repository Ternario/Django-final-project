from django.urls import path, include

urlpatterns = [
    path('auth/', include('booking_project.urls.auth')),
    path('user/', include('booking_project.urls.user')),
    path('categories/', include('booking_project.urls.category')),
    path('placement/', include('booking_project.urls.placement')),
    path('booking/', include('booking_project.urls.booking')),
    path('review/', include('booking_project.urls.reviews')),
]

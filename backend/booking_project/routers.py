from django.urls import path, include

urlpatterns = [
    path('user/', include('booking_project.users.urls')),
    path('placement/', include('booking_project.placement.urls')),
    path('booking/', include('booking_project.booking_info.urls')),
    path('review/', include('booking_project.reviews.urls'))
]
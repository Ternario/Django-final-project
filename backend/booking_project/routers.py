from django.urls import path, include

urlpatterns = [
    path('users/', include('booking_project.users.urls')),
    path('placement/', include('booking_project.placement.urls')),
    path('booking_info/', include('booking_project.booking_info.urls'))
]
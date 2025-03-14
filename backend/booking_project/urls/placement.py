from django.urls import path

from booking_project.views.placement_location import LocationRetrieveUpdateView
from booking_project.views.placement_details import PlacementDetailsRetrieveUpdateView
from booking_project.views.placement_image import ImageListDestroyAPIView, ImageFirstCreateAPIView
from booking_project.views.placement import (
    PlacementCreateView, PlacementListView, PlacementRetrieveUpdateDestroyView, PlacementActivationView
)

urlpatterns = [
    path('', PlacementListView.as_view(), name='placement-list'),
    path('create/', PlacementCreateView.as_view(), name='placement-create'),
    path('create-details/<int:placement>/', PlacementDetailsRetrieveUpdateView.as_view(),
         name='placement-create-details'),
    path('create-images/<int:placement>/', ImageFirstCreateAPIView.as_view(),
         name='placement-create-images'),
    path('<int:pk>/', PlacementRetrieveUpdateDestroyView.as_view(), name='placement'),
    path('<int:pk>/activation/', PlacementActivationView.as_view(), name='placement-activation'),
    path('<int:placement>/details/', PlacementDetailsRetrieveUpdateView.as_view(), name='placement-details'),
    path('<int:placement>/location/', LocationRetrieveUpdateView.as_view(), name='placement-location'),
    path('<int:placement>/images/', ImageListDestroyAPIView.as_view(), name='placement-images'),
]

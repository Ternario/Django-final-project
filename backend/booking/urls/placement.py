from django.urls import path

from booking.views.placement_location import LocationRetrieveUpdateView
from booking.views.placement_details import PlacementDetailsRetrieveUpdateView
from booking.views.placement_image import ImageListDestroyAPIView, ImageFirstCreateAPIView
from booking.views.placement import (
    PlacementCreateView, PlacementsListView, PlacementRetrieveUpdateDestroyView, PlacementActivationView,
    InactivePlacementListView, InactivePlacementRetrieveUpdateDestroyView, MyPlacementsListView
)

urlpatterns = [
    path('', PlacementsListView.as_view(), name='placement-list'),
    path('my/active/', MyPlacementsListView.as_view(), name='my-active-list'),
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
    path('my/inactive/', InactivePlacementListView.as_view(), name='my-inactive-list'),
    path('<int:pk>/inactive/', InactivePlacementRetrieveUpdateDestroyView.as_view(), name="inactive-placement-details")
]

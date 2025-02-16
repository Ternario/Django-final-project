from django.urls import path

from booking_project.views.placement_location import LocationRetrieveUpdateView
from booking_project.views.placement_details import PlacementDetailsRetrieveUpdateView
from booking_project.views.placement_image import ImageRetrieveUpdateAPIView
from booking_project.views.placement import PlacementCreateView, PlacementListView, PlacementRetrieveUpdateDestroyView

urlpatterns = [
    path('create/', PlacementCreateView.as_view(), name="placement-create"),
    path('', PlacementListView.as_view(), name="placement-list"),
    path('<int:pk>/', PlacementRetrieveUpdateDestroyView.as_view(), name="placement"),
    path('<int:placement>/details/', PlacementDetailsRetrieveUpdateView.as_view(), name="placement-details"),
    path('<int:placement>/location/', LocationRetrieveUpdateView.as_view(), name="placement-location"),
    path('<int:placement>/images/', ImageRetrieveUpdateAPIView.as_view(), name="placement-images"),
]

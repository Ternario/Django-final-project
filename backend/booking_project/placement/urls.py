from django.urls import path

from booking_project.placement.views.categories_view import CategoryCreateListView
from booking_project.placement.views.location_view import LocationRetrieveUpdateDestroyView
from booking_project.placement.views.placement_details_view import PlacementDetailsRetrieveUpdateDestroyView
from booking_project.placement.views.placement_view import *

urlpatterns = [
    path('categories/', CategoryCreateListView.as_view(), name="placement-categories"),
    path('create/', PlacementCreateView.as_view(), name="placement-create"),
    path('', PlacementListView.as_view(), name="placement-list"),
    path('<int:pk>/', PlacementRetrieveUpdateDestroyView.as_view(), name="placement"),
    path('details/<int:placement>/', PlacementDetailsRetrieveUpdateDestroyView.as_view(), name="placement-details"),
    path('location/<int:placement>/', LocationRetrieveUpdateDestroyView.as_view(), name="placement-location"),
    path('inactive/', InactivePlacementListView.as_view(), name="placement-inactive"),
    path('inactive/<int:pk>/', InactivePlacementRetrieveUpdateDestroyView.as_view(), name="placement-inactive-details")
]

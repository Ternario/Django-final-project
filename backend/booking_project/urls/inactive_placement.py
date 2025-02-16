from django.urls import path

from booking_project.views.placement import InactivePlacementListView, InactivePlacementRetrieveUpdateDestroyView

urlpatterns = [
    path('inactive/', InactivePlacementListView.as_view(), name="placement-inactive"),
    path('inactive/<int:pk>/', InactivePlacementRetrieveUpdateDestroyView.as_view(), name="placement-inactive-details")
]

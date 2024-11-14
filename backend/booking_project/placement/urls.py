from django.urls import path

from booking_project.placement.views.categories_view import CategoryCreateListView
from booking_project.placement.views.placement_view import PlacementCreateView, PlacementRetrieveUpdateDestroyView, \
    PlacementDetailsRetrieveUpdateDestroyView, LocationRetrieveUpdateDestroyView, PlacementDestroyView

urlpatterns = [
    path('categories/', CategoryCreateListView.as_view(), name="placement-categories"),
    path('create/', PlacementCreateView.as_view(), name="placement-create"),
    path('view/<int:pk>/', PlacementRetrieveUpdateDestroyView.as_view(), name="placement-categories"),
    path('view/', PlacementRetrieveUpdateDestroyView.as_view(), name="placement-categories"),
    path('details/<int:pk>/', PlacementDetailsRetrieveUpdateDestroyView.as_view(), name="placement-categories"),
    path('details/', PlacementDetailsRetrieveUpdateDestroyView.as_view(), name="placement-categories"),
    path('location/<int:pk>/', LocationRetrieveUpdateDestroyView.as_view(), name="placement-categories"),
    path('location/', LocationRetrieveUpdateDestroyView.as_view(), name="placement-categories"),
    path('delete/', PlacementDestroyView.as_view(), name='placement-delete')
]

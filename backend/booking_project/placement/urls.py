from django.urls import path

from booking_project.placement.views.categories_view import CategoryCreateListView
from booking_project.placement.views.placement_view import PlacementView, PlacementCreateView

urlpatterns = [
    path('categories/', CategoryCreateListView.as_view(), name="placement-categories"),
    path('create/', PlacementCreateView.as_view(), name="placement-create"),
    path('<int:pk>/', PlacementView.as_view(), name="placement-categories"),
]

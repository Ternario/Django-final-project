from django.urls import path

from booking_project.placement.views.categories_view import CategoryCreateListView

urlpatterns = [
    path('categories/', CategoryCreateListView.as_view(), name="placement-categories")
]

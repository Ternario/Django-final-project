from django.urls import path

from booking_project.views.category import CategoryCreateListView, CategoryRetrieveUpdateDestroyView

urlpatterns = [
    path('', CategoryCreateListView.as_view(), name="categories"),
    path('<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name="categories-details")
]

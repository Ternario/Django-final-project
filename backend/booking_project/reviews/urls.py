from django.urls import path

from booking_project.reviews.views.review_view import *

urlpatterns = [
    path('', ReviewCreateView.as_view(), name="review-create"),
    path('<int:pk>/', ReviewListView.as_view(), name="review-list"),
    path('update/<int:pk>/', ReviewUpdateView.as_view(), name="review-update"),
    path('delete/<int:pk>/', ReviewDestroyView.as_view(), name="review-delete"),

]

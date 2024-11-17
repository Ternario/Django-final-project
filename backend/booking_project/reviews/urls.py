from django.urls import path

from booking_project.reviews.views.rating_view import *

urlpatterns = [
    path('', ReviewCreateView.as_view(), name="review-create"),
    path('<int:pk>/', ReviewListView.as_view(), name="review-list"),
    path('update/<int:pk>/', ReviewUpdateView.as_view(), name="review-update"),

]

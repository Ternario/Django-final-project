from django.urls import path

from booking.views.review import *

urlpatterns = [
    path('', ReviewCreateView.as_view(), name="review-create"),
    path('<int:pk>/', ReviewListView.as_view(), name="review-list"),
    path('<int:pk>/update/', ReviewUpdateDestroyView.as_view(), name="review-update")

]

from django.urls import path

from properties.views.discount import DiscountPublicRAV, DiscountPublicLAV

urlpatterns = [
    path('', DiscountPublicLAV.as_view(), name='discount-public-list'),
    path('<int:pk>/', DiscountPublicRAV.as_view(), name='discount-public-retrieve'),
]

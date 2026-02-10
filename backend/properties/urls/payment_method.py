from django.urls import path

from properties.views.payment_method import PaymentMethodLAV, PaymentMethodRAV

urlpatterns = [
    path('', PaymentMethodLAV.as_view(), name='pm-list'),
    path('<int:id>/', PaymentMethodRAV.as_view(), name='pm-retrieve')
]

from django.urls import path

from properties.views.payment_type import PaymentTypeLAV, PaymentTypeRAV

urlpatterns = [
    path('', PaymentTypeLAV.as_view(), name='pm-list'),
    path('<int:id>/', PaymentTypeRAV.as_view(), name='pm-retrieve')
]

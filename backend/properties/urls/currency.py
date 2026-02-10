from django.urls import path

from properties.views.currency import CurrencyLAV, CurrencyRAV

urlpatterns = [
    path('', CurrencyLAV.as_view(), name='currency-list'),
    path('<int:id>/', CurrencyRAV.as_view(), name='currency-retrieve')
]

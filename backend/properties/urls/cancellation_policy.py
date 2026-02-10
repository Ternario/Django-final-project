from django.urls import path

from properties.views.cancellation_policy import CancellationPolicyLAV, CancellationPolicyRAV

urlpatterns = [
    path('', CancellationPolicyLAV.as_view(), name='cp-list'),
    path('<int:id>/', CancellationPolicyRAV.as_view(), name='cp-retrieve')
]

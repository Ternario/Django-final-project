from django.urls import path

from properties.views.language import LanguageLAV, LanguageRAV

urlpatterns = [
    path('', LanguageLAV.as_view(), name='language-list'),
    path('<int:id>/', LanguageRAV.as_view(), name='language-retrieve')
]

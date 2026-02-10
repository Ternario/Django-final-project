from rest_framework.routers import DefaultRouter

from properties.views.location_types import CountryMVS, RegionMVS, CityMVS

router = DefaultRouter()

router.register(r'countries/', CountryMVS, basename='countries')
router.register(r'regions/', RegionMVS, basename='regions')
router.register(r'cities/', CityMVS, basename='cities')

urlpatterns = router.urls

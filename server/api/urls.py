from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import OHLCVViewSet, CurrencyPairViewSet

router = DefaultRouter()
router.register(r'ohlcv', OHLCVViewSet, basename='ohlcv')  
router.register(r'pair', CurrencyPairViewSet, basename='pair')  

urlpatterns = [
    path('', include(router.urls)),
]

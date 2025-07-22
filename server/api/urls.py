from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BtcGbpViewSet

router = DefaultRouter()
router.register(r'btc_gbp', BtcGbpViewSet, basename='btc_gbp')

urlpatterns = [
    path('', include(router.urls)),
]

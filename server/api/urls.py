from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import BtcGbpViewSet, EthGbpViewSet, SolGbpViewSet, SuiGbpViewSet

import inspect
import importlib

module = importlib.import_module('.views', package='api')  # Replace with actual package

excluded_class = 'BaseCryptoModel'
all_classes = {
    name: cls for name, cls in inspect.getmembers(module, inspect.isclass)
    if cls.__module__ == module.__name__ and name != excluded_class
}

for name, cls in all_classes.items():
    globals()[name] = cls  # Dynamically injects them into current namespace
    print(type(name))

router = DefaultRouter()


urlpatterns = [
    path('', include(router.urls)),
]

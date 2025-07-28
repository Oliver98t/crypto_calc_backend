from rest_framework import serializers

from .models import models_crypto_classes
import inspect
import importlib

# create serial classes 
serializers_crypto_classes = {}

for model_crypto_class_name in models_crypto_classes:
    class_name = f"{model_crypto_class_name}Serializer"
    model_class = type(
        class_name,
        (serializers.ModelSerializer,),
        {
            '__module__': __name__,  # important for Django internals
            'Meta': type('Meta', (), {
                "model": model_crypto_class_name,
                "fields": '__all__'
            })
        }
    )

    serializers_crypto_classes[class_name] = model_class
    globals()[class_name] = model_class  # make it accessible globally if needed
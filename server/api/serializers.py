from rest_framework import serializers
from .models import BtcGbp

class BtcGbpSerializer(serializers.ModelSerializer):
    class Meta:
        model = BtcGbp
        fields = '__all__'

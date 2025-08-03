from rest_framework import serializers
from .models import CurrencyPair, OHLCV

class CurrencyPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyPair
        fields = '__all__'

class OHLCVSerializer(serializers.ModelSerializer):
    pair = CurrencyPairSerializer(read_only=True)
    pair_id = serializers.PrimaryKeyRelatedField(queryset=CurrencyPair.objects.all(), source='pair', write_only=True)

    class Meta:
        model = OHLCV
        fields = '__all__'
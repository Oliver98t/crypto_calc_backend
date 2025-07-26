from rest_framework import serializers
from .models import BtcGbp, EthGbp, SolGbp, SuiGbp

class BtcGbpSerializer(serializers.ModelSerializer):
    class Meta:
        model = BtcGbp
        fields = '__all__'

class EthGbpSerializer(serializers.ModelSerializer):
    class Meta:
        model = EthGbp
        fields = '__all__'

class SolGbpSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuiGbp
        fields = '__all__'

class SuiGbpSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolGbp
        fields = '__all__'

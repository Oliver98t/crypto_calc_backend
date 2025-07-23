from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import BtcGbp
from .serializers import BtcGbpSerializer
from .CoinDeskAPI.API import CoinDeskAPI
from time import time


class BtcGbpViewSet(viewsets.ModelViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coin_desk_api = CoinDeskAPI()
        self.queryset = BtcGbp.objects.all()
        self.fserializer_class = BtcGbpSerializer
    
    '''
    Update system database using third party store (coin desk API)
    '''
    @action(detail=False, methods=['put'], url_path='update_database')
    def update_database(self, request):
        
        crypto_pair = request.data.get('pair')

        # get most recent data timestamp from local DB
        latest_data = self.queryset.order_by('-id').first()
        latest_DB_timestamp = latest_data.time
        print(latest_DB_timestamp)
        
        # calculate difference from timestamp and now to build query
        current_timestamp = int(time())
        timestamp_diff_seconds = current_timestamp - latest_DB_timestamp
        timestamp_diff_hours = int((timestamp_diff_seconds/60)/60)
        
        # update local DB with new data
        api_data = self.coin_desk_api.get_hourly_data(limit=timestamp_diff_hours)
        new_crypto_data = api_data['Data']['Data']
        
        new_btc_gbp_data = []
        for new_crypto_data_point in new_crypto_data:
            print(new_crypto_data_point)
            new_btc_gbp_data.append( BtcGbp(**new_crypto_data_point) )

        BtcGbp.objects.bulk_create(new_btc_gbp_data)

        return Response(
            {"message": "DB updated successfully"},
            status=status.HTTP_200_OK
            )

    @action(detail=False, methods=['get'], url_path='moving_average')
    def moving_average(self, request):
        # Custom logic here
        return Response({"message": "Recent BTC/GBP data"})


        



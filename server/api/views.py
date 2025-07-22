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
        new_crypto_data = self.coin_desk_api.get_hourly_data(limit=5)
        
        new_row = BtcGbp(   time = 1000,
                            high = 1000,
                            low = 1000,
                            open = 1000,
                            volumefrom = 1000,
                            volumeto = 1000,
                            close = 1000,
                            )
        
        new_rows = [new_row, new_row]
        BtcGbp.objects.bulk_create(new_rows)
        #print(new_crypto_data)

        return Response(
            {"message": "DB updated successfully"},
            status=status.HTTP_200_OK
            )

    @action(detail=False, methods=['get'], url_path='moving_average')
    def moving_average(self, request):
        # Custom logic here
        return Response({"message": "Recent BTC/GBP data"})


        



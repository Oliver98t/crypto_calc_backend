from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from time import time
from math import ceil

from .models import BtcGbp
from .serializers import BtcGbpSerializer
from .CoinDeskAPI.API import CoinDeskAPI, COINDESK_API_HOURLY_LIMIT



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
        # get put request input parameters
        crypto_pair = request.data.get('pair')

        # get most recent data timestamp from local DB
        latest_data = self.queryset.order_by('-id').first()
        latest_DB_timestamp = latest_data.time
        
        # calculate difference from timestamp and now to build query
        current_timestamp = int(time())
        timestamp_diff_seconds = current_timestamp - latest_DB_timestamp
        timestamp_diff_hours = int((timestamp_diff_seconds/60)/60)
        #print(timestamp_diff_hours)
        # calculate number of api calls if limit of 2000 is reached
        hourly_api_calls = ceil(timestamp_diff_hours/COINDESK_API_HOURLY_LIMIT)
        #print(hourly_api_calls)
        # update local DB with new data
        if timestamp_diff_hours > 0:
            for _ in range(hourly_api_calls):
                api_data = self.coin_desk_api.get_hourly_data(limit=timestamp_diff_hours-1)
                new_crypto_data = api_data['Data']['Data']
                
                new_btc_gbp_data = []
                for new_crypto_data_point in new_crypto_data:
                    #print(new_crypto_data_point)
                    new_btc_gbp_data.append( BtcGbp(**new_crypto_data_point) )

                BtcGbp.objects.bulk_create(new_btc_gbp_data)

            return Response(
                {"message": "DB updated successfully"},
                            status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "DB already up to date"},
                status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='moving_average')
    def moving_average(self, request):
        # get to and from timestamps
        to_timestamp = request.data.get('to_ts')
        from_timestamp = request.data.get('from_ts')
        
        if to_timestamp and from_timestamp:
            queryset = self.queryset.filter(time__range=(from_timestamp, to_timestamp))
            print(queryset[0].time)


        
        # Custom logic here
        return Response({"message": "Recent BTC/GBP data"}, 
                                    status=status.HTTP_200_OK)


        



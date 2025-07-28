from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from time import time
from math import ceil
import numpy as np
import pandas as pd

from .models import models_crypto_classes
from .serializers import serializers_crypto_classes
from .CoinDeskAPI.API import CoinDeskAPI, COINDESK_API_HOURLY_LIMIT

# moving average functions
#-------------------------------------------------------------------------
def calculate_ma(df: pd.DataFrame, window_size: int) -> dict:
    # calculate ma column for pandas df
    df.sort_values('time', inplace=True)
    df['ma_price'] = df['price'].rolling(window=window_size).mean().round(2)
    # convert to dict
    # Filter out rows where ma_price is NaN
    filtered_df = df[['time', 'ma_price']].dropna()

    # Convert to list of dictionaries
    result = filtered_df.to_dict(orient='records')

    return result
#-------------------------------------------------------------------------

class BaseViewSet(viewsets.ModelViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.coin_desk_api = CoinDeskAPI()
        self.model = None
        self.basename
    
    @action(detail=False, methods=['put'], url_path='update_database')
    def update_database(self, request):
        # get put request input parameters
        crypto_pair = request.data.get('pair')
        print(self.basename)
        # get most recent data timestamp from local DB
        latest_data = self.queryset.order_by('-id').first()
        latest_DB_timestamp = latest_data.time
        
        # calculate difference from timestamp and now to build query
        current_timestamp = int(time())
        timestamp_diff_seconds = current_timestamp - latest_DB_timestamp
        timestamp_diff_hours = int((timestamp_diff_seconds/60)/60)
        print(f"hourly data points collected: {timestamp_diff_hours}")
        # calculate number of api calls if limit of 2000 is reached
        hourly_api_calls = ceil(timestamp_diff_hours/COINDESK_API_HOURLY_LIMIT)

        # update local DB with new data
        if timestamp_diff_hours > 0:
            for _ in range(hourly_api_calls):
                api_data = self.coin_desk_api.get_hourly_data(limit=timestamp_diff_hours-1)
                new_crypto_data = api_data['Data']['Data']
                
                new_btc_gbp_data = []
                for new_crypto_data_point in new_crypto_data:
                    #print(new_crypto_data_point)
                    new_btc_gbp_data.append( self.model(**new_crypto_data_point) )

                #self.model.objects.bulk_create(new_btc_gbp_data)

            return Response(
                {"message": "DB updated successfully"},
                            status=status.HTTP_200_OK)
        else:
            return Response(
                {"message": "DB already up to date"},
                status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='moving_average')
    def moving_average(self, request):
        # get parameters
        to_timestamp = request.data.get('to_ts')
        from_timestamp = request.data.get('from_ts')
        day_ma = request.data.get('day_ma')
        hour_ma = request.data.get('hour_ma')
        
        # get query set from timestamp range
        if to_timestamp and from_timestamp and ( day_ma or hour_ma ):
            queryset = list(self.queryset.filter(time__range=(from_timestamp, to_timestamp)))
        
        # extract open price data
        prices = [{"time": price.time, "price" : price.open} for price in queryset]
        prices_df = pd.DataFrame(prices)
        
        prices_ma = None
        api_status=status.HTTP_200_OK
        if day_ma:
            day_ma = int(day_ma)
            prices_ma = calculate_ma(df=prices_df,window_size=day_ma*24)
        
        elif hour_ma:
            hour_ma = int(hour_ma)
            prices_ma = calculate_ma(input=prices,window_size=hour_ma)
        
        else:
            api_status = status.HTTP_400_BAD_REQUEST

        # Custom logic here
        return Response({"data": prices_ma}, 
                                    status=api_status)

# dynamically create viewset classes
def viewset_init(model, serializer):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.queryset = model.objects.all()
        self.serializer = serializer
        self.model = model
        self.basename = model._meta.db_table
    return __init__

viewset_crypto_classes = {}
for model_crypto_class_name in models_crypto_classes:
    serializer_class_name = f"{model_crypto_class_name}Serializer"
    class_name = f"{model_crypto_class_name}ViewSet"
    model_class = type(
        class_name,
        (BaseViewSet,),
        {
            '__module__': __name__,  # important for Django internals
            '__init__': viewset_init(model=models_crypto_classes[model_crypto_class_name],
                                     serializer=serializers_crypto_classes[serializer_class_name]),
        }
    )

    viewset_crypto_classes[class_name] = model_class
    globals()[class_name] = model_class  # make it accessible globally if needed
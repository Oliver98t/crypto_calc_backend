from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from time import time
from math import ceil
import numpy as np
import pandas as pd

from .models import OHLCV, CurrencyPair
from .serializers import CurrencyPairSerializer, OHLCVSerializer
from .CoinDeskAPI.API import CoinDeskAPI, COINDESK_API_HOURLY_LIMIT

# moving average functions
#-------------------------------------------------------------------------
def calculate_ma(df: pd.DataFrame, window_size: int) -> dict:
    # calculate ma column for pandas df
    df.sort_values('timestamp', inplace=True)
    df['ma_price'] = df['price'].rolling(window=window_size).mean().round(2)
    # convert to dict
    # Filter out rows where ma_price is NaN
    filtered_df = df[['timestamp', 'ma_price']].dropna()

    # Convert to list of dictionaries
    result = filtered_df.to_dict(orient='records')

    return result
#-------------------------------------------------------------------------
class CurrencyPairViewSet(viewsets.ModelViewSet):
    queryset = CurrencyPair.objects.all()
    serializer_class = CurrencyPairSerializer
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class OHLCVViewSet(viewsets.ModelViewSet):
    queryset = OHLCV.objects.all().order_by('-timestamp')
    serializer_class = OHLCVSerializer
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = OHLCV
        self.OHLCV_hourly_queryset = OHLCV.objects.all().order_by('-timestamp')
        self.currency_pair_queryset = CurrencyPair.objects.all()
        self.serializer_class = OHLCVSerializer
        self.coin_desk_api = CoinDeskAPI()

    @action(detail=False, methods=['put'], url_path='update_database')
    def update_database(self, request):
        # check if crypto/fiat pair exists
        api_status = status.HTTP_200_OK
        crypto_pair = str(request.query_params.get('pair'))
        api_status_message = f"{crypto_pair} pairs updated"
        pair_split = crypto_pair.split('/')
        base = pair_split[0]
        quote = pair_split[1]
        
        try:
            currncy_pair = self.currency_pair_queryset.get(base_code=base, quote_code=quote)
        except CurrencyPair.DoesNotExist:
            api_status = status.HTTP_400_BAD_REQUEST

        # get latest timestamped data
        data = self.OHLCV_hourly_queryset.filter(pair_id=currncy_pair)
        latest_DB_timestamp = data[0].timestamp
        print(f"latest timestamp {latest_DB_timestamp}")
        
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
                api_data = self.coin_desk_api.get_hourly_data(limit=timestamp_diff_hours)
                new_crypto_data = api_data['Data']['Data']
                new_records = []
                for new_crypto_data_point in new_crypto_data:
                    new_record = OHLCV(
                        pair = currncy_pair, 
                        pair_name = crypto_pair,
                        timestamp = new_crypto_data_point['time'],
                        open = new_crypto_data_point['open'],
                        high = new_crypto_data_point['high'],
                        low = new_crypto_data_point['low'],
                        close = new_crypto_data_point['close'],
                        volumeFrom = new_crypto_data_point['volumefrom'],
                        volumeTo = new_crypto_data_point['volumeto']
                    )
                    new_records.append(new_record)

                self.model.objects.bulk_create(new_records, ignore_conflicts=True)

        else:
            api_status_message = f"{crypto_pair} pairs not updated"

        return Response( {"message": api_status_message},
                            status=api_status)
    
    @action(detail=False, methods=['get'], url_path='moving_average')
    def moving_average(self, request):
        # get parameters
        api_status=status.HTTP_200_OK
        # check if crypto/fiat pair exists
        crypto_pair = str(request.query_params.get('pair'))
        print(crypto_pair)
        
        pair_split = crypto_pair.split('/')
        base = pair_split[0]
        quote = pair_split[1]

        try:
            currncy_pair = self.currency_pair_queryset.get(base_code=base, quote_code=quote)
        except CurrencyPair.DoesNotExist:
            api_status = status.HTTP_400_BAD_REQUEST

        to_timestamp = request.query_params.get('to_ts')
        from_timestamp = request.query_params.get('from_ts')
        day_ma = request.query_params.get('day_ma')
        hour_ma = request.query_params.get('hour_ma')

        # get query set from timestamp range
        if to_timestamp and from_timestamp and ( day_ma or hour_ma ):
            currency_pair_queryset = self.OHLCV_hourly_queryset.filter(pair_id=currncy_pair)
            timestamp_range_queryset = currency_pair_queryset.filter(timestamp__range=(from_timestamp, to_timestamp))
            
        
        # extract open price data
        prices = [{"timestamp": price.timestamp, "price" : price.open} for price in timestamp_range_queryset]
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
    
    @action(detail=False, methods=['get'], url_path='available_currencies')
    def available_currencies(self, request):
        api_status=status.HTTP_200_OK
        fiat_currencies = self.currency_pair_queryset.values_list('quote_code',flat=True).distinct()
        crypto_currencies = self.currency_pair_queryset.values_list('base_code',flat=True).distinct()
        print(fiat_currencies)
        print(crypto_currencies)
        data = {}
        data['fiat'] = fiat_currencies
        data['crypto'] = crypto_currencies
        
        return Response({"data": data}, 
                                    status=api_status)
    
    @action(detail=False, methods=['get'], url_path='pair_data')
    def pair_data(self, request):
        # check if crypto/fiat pair exists
        api_status = status.HTTP_200_OK
        crypto_pair = str(request.query_params.get('pair'))
        api_status_message = f"{crypto_pair} data exists"
        pair_split = crypto_pair.split('/')
        base = pair_split[0]
        quote = pair_split[1]
        
        try:
            currncy_pair = self.currency_pair_queryset.get(base_code=base, quote_code=quote)
        except CurrencyPair.DoesNotExist:
            api_status = status.HTTP_400_BAD_REQUEST
        
        to_timestamp = request.query_params.get('to_ts')
        from_timestamp = request.query_params.get('from_ts')

        # get query set from timestamp range
        if to_timestamp and from_timestamp:
            currency_pair_queryset = self.OHLCV_hourly_queryset.filter(pair_id=currncy_pair)
            timestamp_range_queryset = currency_pair_queryset.filter(timestamp__range=(from_timestamp, to_timestamp))
        
        prices = [{"timestamp": price.timestamp, "price" : price.open} for price in timestamp_range_queryset]

        return Response({"data": prices}, 
                                    status=api_status)

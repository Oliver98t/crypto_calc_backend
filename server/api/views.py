from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.request import Request
from time import time
from math import ceil
import inspect
import pandas as pd

from .models import OHLCV, CurrencyPair
from .serializers import CurrencyPairSerializer, OHLCVSerializer
from .CoinDeskAPI.API import CoinDeskAPI, COINDESK_API_HOURLY_LIMIT

# moving average functions
#-------------------------------------------------------------------------
def calculate_ma(df: pd.DataFrame, window_size: int) -> dict:
    # calculate ma column for pandas df
    df.sort_values('timestamp', inplace=True)
    df['price'] = df['price'].rolling(window=window_size).mean().round(2)
    # convert to dict
    # Filter out rows where price is NaN
    filtered_df = df[['timestamp', 'price']].dropna()

    # Convert to list of dictionaries
    result = filtered_df.to_dict(orient='records')

    return result
#-------------------------------------------------------------------------
def calculate_rsi(prices_df: pd.DataFrame, period: int = 14) -> list:
    """
    Calculate RSI for a DataFrame with 'price' and 'timestamp' columns.
    Returns a list of dicts: [{'timestamp': ..., 'rsi': ...}, ...]
    """
    if prices_df.empty or len(prices_df) < period:
        return []

    delta = prices_df['price'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    rsi_df = pd.DataFrame({
        'timestamp': prices_df['timestamp'],
        'rsi': rsi
    }).dropna()

    return rsi_df.to_dict(orient='records')

# TODO populate all DB actions
class DatabaseActions():
    def __init__(   self,
                    model,
                    OHLCV_hourly_queryset,
                    currency_pair_queryset,
                    serializer_class,
                    coin_desk_api):
        
        self.model = model
        self.OHLCV_hourly_queryset = OHLCV_hourly_queryset
        self.currency_pair_queryset = currency_pair_queryset
        self.serializer_class = serializer_class
        self.coin_desk_api = coin_desk_api
    
    def update_database(self, crypto_pair):
        update_database_status = True
        pair_split = crypto_pair.split('/')
        base = pair_split[0]
        quote = pair_split[1]

        try:
            currency_pair = self.currency_pair_queryset.get(base_code=base, quote_code=quote)
        except CurrencyPair.DoesNotExist:
            api_status = status.HTTP_400_BAD_REQUEST
        print(f"{base} {quote}")
        # get latest timestamped data
        data = self.OHLCV_hourly_queryset.filter(pair_id=currency_pair)
        latest_DB_timestamp = data[0].timestamp
        print(f"latest timestamp in DB {latest_DB_timestamp}")

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
                api_data = self.coin_desk_api.get_hourly_data(  limit=timestamp_diff_hours,
                                                                pair={'currency': quote.lower(),'crypto_currency': base.lower()})
                new_crypto_data = api_data['Data']['Data']
                new_records = []
                for new_crypto_data_point in new_crypto_data:
                    new_record = OHLCV(
                        pair = currency_pair,
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
            update_database_status = False
        
        return update_database_status
        


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
        self.database_actions = DatabaseActions(model=self.model,
                                                OHLCV_hourly_queryset=self.OHLCV_hourly_queryset,
                                                currency_pair_queryset=self.currency_pair_queryset,
                                                serializer_class=self.serializer_class,
                                                coin_desk_api=self.coin_desk_api)

    @action(detail=False, methods=['put'], url_path='update_database')
    def update_database_url(self, request):
        # check if crypto/fiat pair exists
        api_status = status.HTTP_200_OK
        crypto_pair = str(request.query_params.get('pair'))
        api_status_message = f"{crypto_pair} pairs updated"
        
        database_update_status = self.database_actions.update_database(crypto_pair=crypto_pair)
        if database_update_status == False:
            api_status = status.HTTP_400_BAD_REQUEST

        return Response( {"message": f"DB updated: {database_update_status}"},
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

    @action(detail=False, methods=['get'], url_path='available_analyses')
    def available_analyses(self, request):
        api_status=status.HTTP_200_OK
        function_prefix = 'calc_'
        analyses = [name.replace(function_prefix, '').replace('_', ' ')
                    for name, obj in inspect.getmembers(OHLCVViewSet, predicate=inspect.isfunction)
                    if name.startswith(function_prefix)]
        # Custom logic here
        return Response({"data": analyses},
                                    status=api_status)

    # TODO gain benchmark
    # TODO cluster database by pair_id
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
            currency_pair = self.currency_pair_queryset.get(base_code=base, quote_code=quote)
        except CurrencyPair.DoesNotExist:
            api_status = status.HTTP_400_BAD_REQUEST

        to_timestamp = request.query_params.get('to_ts')
        from_timestamp = request.query_params.get('from_ts')

        # get query set from timestamp range
        if to_timestamp and from_timestamp:
            currency_pair_queryset = self.OHLCV_hourly_queryset.filter(pair_id=currency_pair)
            timestamp_range_queryset = currency_pair_queryset.filter(timestamp__range=(from_timestamp, to_timestamp))
            timestamp_range_queryset = timestamp_range_queryset.order_by('timestamp')

        prices = [{"timestamp": price.timestamp, "price" : price.open} for price in timestamp_range_queryset]

        return Response({"data": prices},
                                    status=api_status)

    @action(detail=False, methods=['get'], url_path='moving_average')
    def calc_Moving_Average(self, request):
        # get parameters
        api_status=status.HTTP_200_OK
        # check if crypto/fiat pair exists
        crypto_pair = str(request.query_params.get('pair'))
        print(crypto_pair)

        pair_split = crypto_pair.split('/')
        base = pair_split[0]
        quote = pair_split[1]

        try:
            currency_pair = self.currency_pair_queryset.get(base_code=base, quote_code=quote)
        except CurrencyPair.DoesNotExist:
            api_status = status.HTTP_400_BAD_REQUEST

        to_timestamp = request.query_params.get('to_ts')
        from_timestamp = request.query_params.get('from_ts')
        day_ma = request.query_params.get('day_ma')
        hour_ma = request.query_params.get('hour_ma')

        # get query set from timestamp range
        if to_timestamp and from_timestamp and ( day_ma or hour_ma ):
            currency_pair_queryset = self.OHLCV_hourly_queryset.filter(pair_id=currency_pair)
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
            prices_ma = calculate_ma(df=prices_df,window_size=hour_ma)

        else:
            api_status = status.HTTP_400_BAD_REQUEST

        # Custom logic here
        return Response({"data": prices_ma},
                                    status=api_status)

    @action(detail=False, methods=['get'], url_path='market_sentiment')
    def calc_Market_Sentiment(self, request: Request):
        api_status=status.HTTP_200_OK
        # check if crypto/fiat pair exists
        crypto_pair = str(request.query_params.get('pair'))
        to_ts = request.query_params.get('to_ts')
        search_string = request.query_params.get('search_string')

        sentiment_data_set = self.coin_desk_api.get_sentiment(search_string=search_string)
        # extract sentiment scores
        sentiment_data_set_len = len(sentiment_data_set)
        sentiment_total = 0
        for sentiment_data in sentiment_data_set:
            current_sentiment = sentiment_data['SENTIMENT']
            print(current_sentiment)
            if current_sentiment == "POSITIVE":
                sentiment_total += 1
            elif current_sentiment == "NEUTRAL":
                sentiment_total += 0
            elif current_sentiment == "NEGATIVE":
                sentiment_total -= 1
        
        sentiment_score = sentiment_total/sentiment_data_set_len
        
        
        # Custom logic here
        return Response({"data": {"sentiment_score": sentiment_score,
                                  "from_ts" : sentiment_data_set[-1]['PUBLISHED_ON'],
                                  "to_ts" : sentiment_data_set[0]['PUBLISHED_ON']}},
                                    status=api_status)

    @action(detail=False, methods=['get'], url_path='rsi')
    def calc_RSI(self, request):
        # check if crypto/fiat pair exists
        api_status = status.HTTP_200_OK
        crypto_pair = str(request.query_params.get('pair'))
        api_status_message = f"{crypto_pair} data exists"
        pair_split = crypto_pair.split('/')
        base = pair_split[0]
        quote = pair_split[1]

        # get interval
        interval = request.query_params.get('interval')
        print(interval)

        try:
            currency_pair = self.currency_pair_queryset.get(base_code=base, quote_code=quote)
        except CurrencyPair.DoesNotExist:
            api_status = status.HTTP_400_BAD_REQUEST

        to_timestamp = request.query_params.get('to_ts')
        from_timestamp = request.query_params.get('from_ts')

        # get query set from timestamp range
        if to_timestamp and from_timestamp:
            currency_pair_queryset = self.OHLCV_hourly_queryset.filter(pair_id=currency_pair)
            timestamp_range_queryset = currency_pair_queryset.filter(timestamp__range=(from_timestamp, to_timestamp))
            timestamp_range_queryset = timestamp_range_queryset.order_by('timestamp')


        prices = [{"timestamp": price.timestamp, "price" : price.open} for price in timestamp_range_queryset]
        prices_df = pd.DataFrame(prices)

        # Calculate RSI values
        rsi_period = int(request.query_params.get('period', 14))  # default to 14 if not provided
        # If period is in days and data is hourly, multiply by 24
        rsi_period_points = rsi_period * 24  # 14 days * 24 hours = 336 points
        rsi_values = calculate_rsi(prices_df)

        return Response({"data": rsi_values},
                                    status=api_status)
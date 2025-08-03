'''
standalone script for updating the DB
'''
import os
import django
from time import time
import csv

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from api.CoinDeskAPI.API import CoinDeskAPI 
from api.models import CurrencyPair, OHLCV, CRYPTOS, FIATS

API_CALLS = 50

def insert_currency_pairs():
    for crypto in CRYPTOS:
        for fiat in FIATS:
            CurrencyPair.objects.get_or_create(
                base_code=crypto,
                quote_code=fiat
            )

def insert_ohlcv_data_pair(base : str, quote : str, coin_desk_api : CoinDeskAPI):
    pair, _ = CurrencyPair.objects.get_or_create(base_code=base, quote_code=quote)
    crypto_pair = {'currency': quote.lower(), 'crypto_currency': base.lower()}
    current_timestamp = int(time())

    new_records = []
    print(f"uploading {base}/{quote}")
    for api_call in range(API_CALLS):
        coin_data = coin_desk_api.get_hourly_data(unix_timestamp=current_timestamp, pair=crypto_pair)['Data']
        Time_from = coin_data['TimeFrom']
        current_timestamp = Time_from
        data = coin_data['Data']
        
        for data_point in data:
            new_record = OHLCV(
                pair=pair,
                pair_name = f"{base}/{quote}",
                timestamp = data_point['time'],
                open = data_point['open'],
                high = data_point['high'],
                low = data_point['low'],
                close = data_point['close'],
                volumeFrom = data_point['volumefrom'],
                volumeTo = data_point['volumeto']
            )
            new_records.append(new_record)
        print(f"{api_call+1} / {API_CALLS} completed")
    OHLCV.objects.bulk_create(new_records[::-1], ignore_conflicts=True)
    print(f"{base}/{quote} records uploaded to DB")
        
def insert_ohlcv_data():
    coin_desk_api = CoinDeskAPI()
    for crypto in CRYPTOS:
        for fiat in FIATS:
            insert_ohlcv_data_pair(base=crypto, quote=fiat, coin_desk_api=coin_desk_api)

if __name__ == "__main__":
    insert_ohlcv_data()

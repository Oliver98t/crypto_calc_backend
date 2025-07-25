from API import CoinDeskAPI
from time import time
import csv
import pandas as pd
from sqlalchemy import create_engine

API_CALLS = 50

def write_crypto_data_to_csv(filename: str, pair):
    coin_desk_api = CoinDeskAPI()
    current_timestamp = int(time())
    column_name_lock = False
    with open(f"{filename}", "a", newline="") as csvfile:
        for api_call in range(API_CALLS):
            coin_data = coin_desk_api.get_hourly_data(unix_timestamp=current_timestamp, pair=pair)['Data']
            Time_from = coin_data['TimeFrom']
            current_timestamp = Time_from
            data = coin_data['Data']
            
            if column_name_lock == False:
                writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                writer.writeheader()

            writer.writerows(data)
            column_name_lock = True

def ingest_csv_to_db(filepath, table_name):
    user = 'oli98'
    password = 'password'
    port = 5432
    db = "postgres"

    df = pd.read_csv(filepath, low_memory=False)
    df.sort_values("time", ascending=True, inplace=True)
    engine = create_engine(f'postgresql://{user}:{password}@localhost:{port}/{db}')
    df.to_sql(table_name, engine, if_exists='append', index=False, chunksize=1000)

    
if __name__ == "__main__":
    data_filepath = "data/"
    
    cryptos = ['eth', 'sol', 'sui']
    for crypto in cryptos:
        #write_crypto_data_to_csv(filename=f"{data_filepath}/{crypto}_gbp.csv", pair={'currency': 'gbp', 'crypto_currency': crypto})
        pair = f"{crypto}_gbp"
        ingest_csv_to_db(f'{data_filepath}/{pair}.csv', table_name=pair)


    
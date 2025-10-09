import requests
import argparse
from time import time

# Endpoint and parameters
IP = "192.168.1.73"
BASE_URL = f"http://{IP}/api/ohlcv/"
TIMEOUT_S = 5

def get_system_status():
    url = BASE_URL + "get_system_status/"
    
    headers = {"Accept": "application/json"}
    # Perform GET request
    response = requests.get(url, headers=headers, timeout=TIMEOUT_S)

    # Check status and display result
    if response.status_code == 200:
        data = response.json()
        print(f"system status {data}")
    else:
        print(f"Error {response.status_code}: {response.text}")

def get_ma(pair: str):
    url = BASE_URL + "moving_average/"
    params = {
        "pair": pair,
        "from_ts": 1690958435,
        "to_ts": 1722580835,
        "day_ma": 10
    }
    headers = {"Accept": "application/json"}
    # Perform GET request
    response = requests.get(url, params=params, headers=headers)

    # Check status and display result
    if response.status_code == 200:
        data = response.json()
        print("Moving Average Data:")
        print(data)
    else:
        print(f"Error {response.status_code}: {response.text}")

def get_currencies() -> dict:
    url = BASE_URL + "available_currencies/"

    headers = {"Accept": "application/json"}
    # Perform GET request
    response = requests.get(url, headers=headers)

    # Check status and display result
    if response.status_code == 200:
        data = response.json()
        #print("Available currencies:")
        #print(data)
    else:
        print(f"Error {response.status_code}: {response.text}")

    return data

def get_pair_data(pair: str, from_ts: int, to_ts: int):
    url = BASE_URL + "pair_data/"
    params = {
        "pair": pair,
        "from_ts": from_ts,
        "to_ts": to_ts
    }
    headers = {"Accept": "application/json"}
    # Perform GET request
    start_time = time()
    response = requests.get(url, headers=headers, params=params)
    end_time = time()
    elapsed_time = end_time - start_time

    # Check status and display result
    if response.status_code == 200:
        data = response.json()
        #print(data)
    else:
        print(f"Error {response.status_code}: {response.text}")

def update_pair(pair: str):
    url = BASE_URL + "update_database/"
    params = {
        "pair": pair
    }
    headers = {"Accept": "application/json"}
    # Perform GET request
    response = requests.put(url, headers=headers, params=params)

    # Check status and display result
    if response.status_code == 200:
        data = response.json()
        print("Available currencies:")
        print(data)
    else:
        print(f"Error {response.status_code}: {response.text}")

def update_all_pairs():
    data = get_currencies()
    currencies = data['data']
    cryptos = currencies['crypto']
    fiats = currencies['fiat']

    for crypto in cryptos:
        for fiat in fiats:
            pair_string = f"{crypto}/{fiat}"
            update_pair(pair=pair_string)

def get_rsi(pair: str, from_ts: int, to_ts: int):
    url = BASE_URL + "rsi/"
    params = {
        "pair": pair,
        "from_ts": from_ts,
        "to_ts": to_ts,
    }
    headers = {"Accept": "application/json"}
    # Perform GET request
    response = requests.get(url, params=params, headers=headers)
    
    # Check status and display result

    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Error {response.status_code}: {response.text}")

def get_market_sentiment(pair: str, to_ts: int, search_string: str):
    url = BASE_URL + "market_sentiment/"
    params = {
        "pair": pair,
        "to_ts": to_ts,
        "search_string": search_string
    }
    headers = {"Accept": "application/json"}
    # Perform GET request
    response = requests.get(url, params=params, headers=headers)
    
    # Check status and display result
    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Error {response.status_code}: {response.text}")

def get_benchmark():
    currencies = get_currencies().get('data')
    cryptos = currencies.get('crypto')
    fiats = currencies.get('fiat')
    from_ts = 1600444665
    to_ts = 1758214665
    start_time = time()
    repeat_num = 1
    for _ in range(repeat_num):
        for crypto in cryptos:
            for fiat in fiats:
                pair = f"{crypto}/{fiat}"
                get_pair_data(pair=pair, from_ts=from_ts, to_ts=to_ts)
        end_time = time()
        elapsed_time = end_time - start_time
        print(elapsed_time)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Crypto Calc API endpoints.")
    parser.add_argument('--ma', metavar='PAIR', help='Test moving average for given pair (e.g. BTC/GBP)\n')
    parser.add_argument('--rsi', nargs=3, metavar=('PAIR', 'FROM_TS', 'TO_TS'), help='Test pair data endpoint\n')
    parser.add_argument('--currencies', action='store_true', help='Test available currencies endpoint')
    parser.add_argument('--status', action='store_true', help='Test check if system is alive')
    parser.add_argument('--benchmark', action='store_true', help='Get benchmark time for pair data')
    parser.add_argument('--pair-data', nargs=3, metavar=('PAIR', 'FROM_TS', 'TO_TS'), help='Test pair data endpoint')
    parser.add_argument('--update-pair', metavar='PAIR', help='Test update database for a specific pair')
    parser.add_argument('--update-all', action='store_true', help='Test update database for all pairs')
    parser.add_argument('--market-sentiment', nargs=3, metavar=('PAIR', 'TO_TS', 'SEARCH_STRING'), help='Get market sentiment')

    args = parser.parse_args()
    if args.benchmark:
        get_benchmark()
    if args.status:
        get_system_status()
    if args.market_sentiment:
        pair, to_ts, search_string = args.market_sentiment
        get_market_sentiment(pair=pair, to_ts=to_ts, search_string=search_string)
    if args.ma:
        get_ma(args.ma)
    if args.rsi:
        get_rsi(pair=args.rsi[0], from_ts=args.rsi[1], to_ts=args.rsi[2])
    if args.currencies:
        get_currencies()
    if args.pair_data:
        pair, from_ts, to_ts = args.pair_data
        get_pair_data(pair=pair, from_ts=int(from_ts), to_ts=int(to_ts))
    if args.update_pair:
        update_pair(args.update_pair)
    if args.update_all:
        update_all_pairs()
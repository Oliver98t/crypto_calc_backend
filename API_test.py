import requests

# Endpoint and parameters
BASE_URL = "http://localhost:8000/ohlcv/"

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
        print("Available currencies:")
        print(data)
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
    response = requests.get(url, headers=headers, params=params)

    # Check status and display result
    if response.status_code == 200:
        data = response.json()
        print("Available currencies:")
        print(data)
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

if __name__ == "__main__":
    #get_ma("BTC/GBP")
    #get_currencies()
    get_pair_data(pair='BTC/GBP', from_ts=1690958435, to_ts=1722580835)
    #update_pair('SOL/GBP')
    #update_all_pairs()


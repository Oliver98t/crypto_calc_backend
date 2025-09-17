import pytest
from tests.API_test import get_currencies

def test_get_currencies():
    expected = {'data': {'fiat': ['GBP', 'USD', 'EUR'], 'crypto': ['SUI', 'BTC', 'SOL', 'ETH']}}
    results = get_currencies()
    assert expected == results
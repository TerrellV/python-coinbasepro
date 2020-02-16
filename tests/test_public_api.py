import pytest

import requests
from decimal import Decimal
from coinbase_pro import CBProPublic, CBProAuthenticated
from coinbase_pro.api import API
from datetime import datetime

@pytest.fixture
def live_base_api():
    return API('https://api.pro.coinbase.com/')


@pytest.fixture
def live_public_api():
    sandbox_mode = False
    return CBProPublic(sandbox_mode=False)


def test_exchange_time(live_public_api):
    exchange_time = live_public_api.exchange_time()

    assert type(exchange_time) == str
    assert type(datetime.fromisoformat(exchange_time)) == datetime
    assert datetime.strptime(exchange_time, '%Y-%m-%d %H:%M:%S.%f')

def test_api_failure(live_base_api):
    with pytest.raises(requests.HTTPError):
        live_base_api.get('fake_endpoint')

def test_trading_pairs(live_public_api):
    trading_pairs = live_public_api.trading_pairs()

    assert type(trading_pairs) == list
    assert len(trading_pairs) > 0
    assert all([pair in trading_pairs for pair in ['BTC-USD', 'ETH-USD', 'LTC-USD']])

def test_get_exchange_rate(live_public_api):
    # confirm a string is returned
    # confirm the string can be converted to a decimal

    product_id = 'ETH-BTC'
    price = live_public_api.exchange_rate(product_id)

    assert type(price) == str
    assert type(Decimal(price)) == Decimal
    assert price == requests.get(f'https://api.pro.coinbase.com/products/{product_id}/ticker').json()['price']

def test_get_asset_usd_price(live_public_api):
    # confirm a string is returned
    # confirm the string can be converted to a decimal

    symbol = 'ETH'
    price = live_public_api.usd_price(symbol)

    assert type(price) == str
    assert type(Decimal(price)) == Decimal
    assert price == requests.get(f'https://api.pro.coinbase.com/products/{symbol}-USD/ticker').json()['price']
    

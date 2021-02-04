from decimal import Decimal
from datetime import datetime
import types

import pytest
import requests

from cbp_client import PublicAPI
from cbp_client.api import API
from cbp_client.product import Product


@pytest.fixture
def live_base_api():
    return API(sandbox_mode=False)


@pytest.fixture
def live_public_api():
    return PublicAPI(sandbox_mode=False)


def test_currencies_and_products(live_public_api):

    assert live_public_api._products
    assert live_public_api.currencies


def test_twenty_four_hour_stats(live_public_api):
    stats = live_public_api.twenty_four_hour_stats('XLM-USD')
    actual_keys = set(stats.keys())
    expected_keys = {'high', 'low', 'volume', 'open', 'volume_30day', 'last'}

    assert isinstance(stats, dict)
    assert actual_keys == expected_keys


def test_exchange_time(live_public_api):
    exchange_time = live_public_api.exchange_time()

    assert type(exchange_time) == str
    assert type(datetime.fromisoformat(exchange_time)) == datetime
    assert datetime.strptime(exchange_time, '%Y-%m-%d %H:%M:%S.%f')


def test_products(live_public_api):

    api = live_public_api

    products = api._products
    # assert api._products == List[Product()...]
    assert isinstance(products, list)
    assert all(isinstance(p, Product) for p in products)

    # expecting to only get products that are live
    expected_products = [p for p in products if p.live]
    assert api.products(live=True) == expected_products

    # expecting to only get products where fully_tradeable=True
    expected_products = [p for p in products if p.fully_tradeable]
    assert api.products(fully_tradeable=True) == expected_products

    # expecting to only get products where quote_currency=BTC
    expected_products = [p for p in products if p.quote_currency == 'BTC']
    assert api.products(quote_currency='btc') == expected_products

    # expecting to only get products where quote_currency=BTC and min_market_funds=10
    expected_products = [p for p in products if p.quote_currency == 'USD'
                                             and p.min_market_funds == '10']

    assert api.products(quote_currency='usd', min_market_funds=10) == expected_products


def test_price(live_public_api):
    # confirm a string is returned
    # confirm the string can be converted to a decimal

    symbol = 'ETH'
    price = live_public_api.price(symbol)

    assert type(price) == str
    assert type(Decimal(price)) == Decimal

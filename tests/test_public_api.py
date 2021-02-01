from decimal import Decimal
from datetime import datetime
import types

import pytest
import requests

from cbp_client import PublicAPI
from cbp_client.api import API


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


@pytest.mark.parametrize(
    'kwargs, expected_products',
    [
        ({'random': 'test'}, []),
        ({'live': True}, ['001', '002']),
        ({'fully_tradeable': True}, ['001']),
        ({'live': False}, ['003'])
    ]
)
def test_products(live_public_api, expected_products, kwargs):
    # FakeProduct = (
    # namedtuple('FakeProduct', 'uid, id, fully_tradeable, live, quote, base'))

    # live_public_api._products = [
    #     FakeProduct(**{
    #         'uid': '001',
    #         'id': 'BTC-USD',
    #         'fully_tradeable': True,
    #         'live': True,
    #         'quote': 'USD',
    #         'base': 'BTC'
    #     }),
    #     FakeProduct(**{
    #         'uid': '002',
    #         'id': 'ETH-USD',
    #         'fully_tradeable': False,
    #         'live': True,
    #         'quote': 'USD',
    #         'base': 'ETH'
    #     }),
    #     FakeProduct(**{
    #         'uid': '003',
    #         'id': 'ETH-BTC',
    #         'fully_tradeable': False,
    #         'live': False,
    #         'quote': 'BTC',
    #         'base': 'ETH'
    #     })
    # ]
    actual_products = live_public_api.products(**kwargs)

    # expected = [
    #     p
    #     for p in live_public_api._products
    #     if p.uid in expected_products
    # ]
    assert isinstance(actual_products, types.GeneratorType)
    # assert list(actual_products) == expected


def test_price(live_public_api):
    # confirm a string is returned
    # confirm the string can be converted to a decimal

    symbol = 'ETH'
    price = live_public_api.price(symbol)

    assert type(price) == str
    assert type(Decimal(price)) == Decimal

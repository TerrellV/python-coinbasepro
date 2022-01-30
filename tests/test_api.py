
import json
import pathlib
import time
import random

import pytest
import requests

from cbp_client.api import API
from cbp_client.auth import Auth
from cbp_client.helpers import load_credentials


@pytest.fixture
def live_base_api():
    return API(sandbox_mode=False)


@pytest.fixture
def sandbox_base_api():
    return API(sandbox_mode=True)


def test_api_post(sandbox_base_api):
    data = {
        'type': 'market',
        'side': 'buy',
        'product_id': 'BTC-USD',
        'funds': '10'
    }
    auth = Auth(**load_credentials(sandbox_mode=True))
    r = sandbox_base_api.post('orders', data=data, auth=auth)

    assert r.url == 'https://api-public.sandbox.exchange.coinbase.com/orders'
    assert r.status_code == 200
    time.sleep(random.uniform(0.3, 0.4))


def test_api_get(live_base_api):
    r = live_base_api.get('/products')

    assert r.url == 'https://api.exchange.coinbase.com/products'
    assert r.status_code == 200
    time.sleep(random.uniform(0.3, 0.4))


def test_api_failure(live_base_api):
    with pytest.raises(requests.HTTPError):
        live_base_api.get('fake_endpoint')
        time.sleep(random.uniform(0.3, 0.4))

    with pytest.raises(requests.HTTPError):
        live_base_api.post('fake_endpoint', auth=None)
        time.sleep(random.uniform(0.3, 0.4))

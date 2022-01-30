
import json
import pathlib
import time
import random

import pytest
import requests

from cbp_client.api import API
from cbp_client.auth import Auth


@pytest.fixture
def live_base_api():
    return API(sandbox_mode=False)


@pytest.fixture
def sandbox_base_api():
    return API(sandbox_mode=True)


@pytest.fixture
def sandbox_creds():
    def func():
        try:
            return json.loads(pathlib.Path('credentials.json').read_text())['sandbox']
        except FileNotFoundError:
            return None

    return func


def test_api_post(sandbox_base_api, sandbox_creds):
    data = {
        'type': 'market',
        'side': 'buy',
        'product_id': 'BTC-USD',
        'funds': '10'
    }
    auth = Auth(**sandbox_creds())
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

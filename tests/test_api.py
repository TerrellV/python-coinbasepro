import pytest

import json, pathlib

import requests
from decimal import Decimal
from cbp_client import CBProPublic, CBProAuthenticated
from cbp_client.api import API
from datetime import datetime


@pytest.fixture
def live_base_api():
    return API('https://api.pro.coinbase.com/')

@pytest.fixture
def live_public_api():
    return CBProPublic(sandbox_mode=False)

@pytest.fixture
def live_auth_api():
    return CBProAuthenticated(
        json.loads(pathlib.Path('credentials.json').read_text())['sandbox'],
        sandbox_mode=True
    )


def test_currencies_and_products(live_public_api):

    assert live_public_api.products
    assert live_public_api.currencies


def test_api_failure(live_base_api):
    with pytest.raises(requests.HTTPError):
        live_base_api.get('fake_endpoint')

def test_pagination(live_auth_api):
    pass
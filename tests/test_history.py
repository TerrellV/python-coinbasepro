import pytest

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

def test_currencies_and_products(live_public_api):

    assert live_public_api.products
    assert live_public_api.currencies











    

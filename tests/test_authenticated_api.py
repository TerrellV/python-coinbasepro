import pytest
import json
import pathlib
from decimal import Decimal

import requests
from decimal import Decimal
from cbp_client import CBProPublic, CBProAuthenticated
from cbp_client.api import API
from datetime import datetime


@pytest.fixture
def live_base_api():
    return API('https://api.pro.coinbase.com/')


@pytest.fixture
def live_auth_api():
    return CBProAuthenticated(
        json.loads(pathlib.Path('credentials.json').read_text())['sandbox'],
        sandbox_mode=True
    )


def test_market_buy(live_auth_api):

    purchase_amount = 10

    coin_to_purchase = 'BTC'

    starting_balance = sum(Decimal(a['balance']) for a in live_auth_api.accounts if a['currency'] == coin_to_purchase)
    response = live_auth_api.market_buy(purchase_amount, f'{coin_to_purchase}-USD', delay=False).json()
    live_auth_api.refresh_accounts()
    ending_balance = sum(Decimal(a['balance']) for a in live_auth_api.accounts if a['currency'] == coin_to_purchase)


    assert response['side'] == 'buy'
    assert int(response['specified_funds']) == purchase_amount
    assert response['type'] == 'market'
    assert ending_balance > starting_balance

    assert live_auth_api.cb_public.api.base_url == 'https://api-public.sandbox.pro.coinbase.com/'
    assert live_auth_api.api.base_url == 'https://api-public.sandbox.pro.coinbase.com/'


def test_market_sell(live_auth_api):

    sale_quantity = Decimal('0.01')

    coin_to_purchase = 'BTC'

    starting_balance = sum(Decimal(a['balance']) for a in live_auth_api.accounts if a['currency'] == coin_to_purchase)
    response = live_auth_api.market_sell(sale_quantity, f'{coin_to_purchase}-USD', delay=False).json()
    live_auth_api.refresh_accounts()
    ending_balance = sum(Decimal(a['balance']) for a in live_auth_api.accounts if a['currency'] == coin_to_purchase)

    assert response['side'] == 'sell'
    assert Decimal(response['size']) == sale_quantity
    assert response['type'] == 'market'
    assert ending_balance < starting_balance

    assert live_auth_api.cb_public.api.base_url == 'https://api-public.sandbox.pro.coinbase.com/'
    assert live_auth_api.api.base_url == 'https://api-public.sandbox.pro.coinbase.com/'
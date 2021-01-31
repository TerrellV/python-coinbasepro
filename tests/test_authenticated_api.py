import pytest
import json
import pathlib
from decimal import Decimal


from cbp_client import AuthAPI
from cbp_client.api import API


SANDBOX_URL = 'https://api-public.sandbox.pro.coinbase.com'


@pytest.fixture
def live_base_api():
    return API(sandbox_mode=False)


@pytest.fixture
def sandbox_auth_api():
    return AuthAPI(
        json.loads(pathlib.Path('credentials.json').read_text())['sandbox'],
        sandbox_mode=True
    )


def test_market_buy(sandbox_auth_api):

    assert sandbox_auth_api.api.base_url == SANDBOX_URL
    purchase_amount = 10

    coin_to_purchase = 'BTC'

    starting_balance = sum(
        Decimal(a.balance)
        for a in sandbox_auth_api.accounts
        if a.currency.upper() == coin_to_purchase
    )

    r = sandbox_auth_api.market_buy(
        funds=purchase_amount,
        product_id=f'{coin_to_purchase}-USD',
        delay=False
    ).json()

    sandbox_auth_api.refresh_accounts()

    ending_balance = sum(
        Decimal(a.balance)
        for a in sandbox_auth_api.accounts
        if a.currency.upper() == coin_to_purchase
    )

    assert r['side'] == 'buy'
    assert int(r['specified_funds']) == purchase_amount
    assert r['type'] == 'market'
    assert ending_balance > starting_balance


def test_market_sell(sandbox_auth_api):

    assert sandbox_auth_api.api.base_url == SANDBOX_URL

    sale_quantity = Decimal('0.01')
    coin_to_purchase = 'BTC'

    starting_balance = sum(
        Decimal(a.balance)
        for a in sandbox_auth_api.accounts
        if a.currency.upper() == coin_to_purchase
    )

    r = sandbox_auth_api.market_sell(
        size=sale_quantity,
        product_id=f'{coin_to_purchase}-USD',
        delay=False
    ).json()

    sandbox_auth_api.refresh_accounts()

    ending_balance = sum(
        Decimal(a.balance)
        for a in sandbox_auth_api.accounts
        if a.currency.upper() == coin_to_purchase
    )

    assert r['side'] == 'sell'
    assert Decimal(r['size']) == sale_quantity
    assert r['type'] == 'market'
    assert ending_balance < starting_balance


def test_balance(sandbox_auth_api):
    api = sandbox_auth_api
    bal = api.balance('btc')
    eth_bal = api.balance('eth')

    assert isinstance(bal, str)
    assert api.balance('BTC') == bal
    assert api.balance('bTc') == bal
    assert isinstance(eth_bal, str)
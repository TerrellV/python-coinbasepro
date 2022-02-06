import pytest
from decimal import Decimal
from datetime import datetime, timedelta, date
import types

from cbp_client import AuthAPI
from cbp_client.api import API


SANDBOX_URL = 'https://api-public.sandbox.exchange.coinbase.com'


@pytest.fixture
def live_base_api():
    return API(sandbox_mode=False)


@pytest.fixture
def sandbox_auth_api():
    return AuthAPI(sandbox_mode=True)


def test_market_buy(sandbox_auth_api):

    assert sandbox_auth_api.api.base_url == SANDBOX_URL
    purchase_amount = 15

    coin_to_purchase = 'BTC'

    starting_balance = sum(
        Decimal(a.balance)
        for a in sandbox_auth_api._accounts
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
        for a in sandbox_auth_api._accounts
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
        for a in sandbox_auth_api._accounts
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
        for a in sandbox_auth_api._accounts
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


def test_accounts(sandbox_auth_api):
    btc_act = sandbox_auth_api.accounts(currency='BTC')
    all_accounts = sandbox_auth_api.accounts()

    assert btc_act.currency == 'BTC'
    assert btc_act.id
    assert len(all_accounts) > 0


def test_account_history(sandbox_auth_api):

    btc_account = sandbox_auth_api.accounts(currency='BTC')
    account_id = btc_account.id

    hist = sandbox_auth_api.api.get_paginated_endpoint(
        endpoint=f'accounts/{account_id}/ledger',
        auth=sandbox_auth_api.auth,
        start_date=(datetime.now() - timedelta(days=730)).isoformat()
    )

    assert isinstance(hist, types.GeneratorType)

    for i in range(3):
        next(hist)


def test_orders(sandbox_auth_api):
    n_days_prior = '2018-01-01'
    end_date = (date.today() - timedelta(days=4)).isoformat()

    sandbox_auth_api = AuthAPI(sandbox_mode=False)

    all_orders = list(sandbox_auth_api.orders(
        start_date=n_days_prior,
        end_date=end_date,
    ))
    settled_orders = list(sandbox_auth_api.orders(
        start_date=n_days_prior,
        end_date=end_date,
        settled=True
    ))
    done_orders = list(sandbox_auth_api.orders(
        start_date=n_days_prior,
        end_date=end_date,
        status='done'
    ))

    assert len(list(all_orders)) > 0
    assert all(o['settled'] for o in settled_orders)
    assert all(o['status'] == 'done' for o in done_orders)

    def convert_coinbase_datetime(coinbase_datetime_str):
        dt_string = coinbase_datetime_str.split('.')[0].strip('Z')
        return datetime.strptime(dt_string, '%Y-%m-%dT%H:%M:%S').date().isoformat()

    # check done at is after start date
    assert all(convert_coinbase_datetime(o['done_at']) >= n_days_prior for o in all_orders)
    assert all(convert_coinbase_datetime(o['done_at']) >= n_days_prior for o in done_orders)
    assert all(convert_coinbase_datetime(o['done_at']) >= n_days_prior for o in settled_orders)

    # check done at is before end date
    assert all(convert_coinbase_datetime(o['done_at']) <= end_date for o in all_orders)
    assert all(convert_coinbase_datetime(o['done_at']) <= end_date for o in done_orders)
    assert all(convert_coinbase_datetime(o['done_at']) <= end_date for o in settled_orders)


def test_payment_methods(sandbox_auth_api):

    all_methods = sandbox_auth_api.payment_methods()
    usd_wallet = sandbox_auth_api.payment_methods(name='USD Wallet')

    assert len(all_methods) > 1
    assert usd_wallet['name'].lower() == 'usd wallet'


def test_deposit(sandbox_auth_api):
    amount = 10
    currency = 'USD'
    payment_method = (
        sandbox_auth_api.payment_methods(name='TD Bank ******2778')
    )
    r = sandbox_auth_api.deposit(
        amount=amount,
        currency=currency,
        payment_method_id=payment_method['id']
    )
    data = r.json()

    assert r.status_code == 200
    assert float(data['amount']) == float(amount)
    assert data['currency'] == currency


def test_profile(sandbox_auth_api):
    '''
    >>> api.this_profile
    {required_keys}

    required_keys: id, user_id, name, active, is_default, created_at
    '''
    api = sandbox_auth_api
    expected_profile = {
        'id': '9a0445ac-7d5e-4261-a8cb-5840fd655b48',
        'user_id': '59c9f79cb6ea17011a46b3e2',
        'name': 'default',
        'active': True,
        'is_default': True,
        'created_at': '2019-03-23T21:14:19.442971Z'
    }
    actual_profile = api.profile
    actual_keys = actual_profile.keys()
    actual_values = actual_profile.values()

    # at least expected keys returned... ok if more
    assert all([
        key in actual_keys
        for key in expected_profile.keys()
    ])

    # at least expected values returned... ok if more
    assert all([
        val in actual_values
        for val in expected_profile.values()
    ])


def test_get_profiles(sandbox_auth_api):
    '''
    >>> api.get_profiles()
    [{required_keys...}, {required_keys...}, ...]
    required keys: id, user_id, name, active, is_default, created_at
    '''

    expected_keys = ['id', 'user_id', 'name', 'active', 'is_default', 'created_at']
    api = sandbox_auth_api
    profiles = api.get_profiles()
    all([
        k in expected_keys
        for profile in profiles
        for k in profile.keys()
    ])

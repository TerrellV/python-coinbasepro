import pytest

import requests

from coinbase_pro import CBProPublic, CBProAuthenticated
from coinbase_pro.api import API



def test_get_asset_usd_price():
    # confirm a string is returned
    # confirm the string can be converted to a float
    # confirm an exception is raised when an invalid symbol is used
    sandbox_mode = False

    LIVE_URL = 'https://api.pro.coinbase.com/'
    SANDBOX_URL = 'https://api-public.sandbox.pro.coinbase.com/'

    base_url = SANDBOX_URL if sandbox_mode else LIVE_URL

    working_symbol = 'eth'
    unvalid_symbol = '#$@#'

    cb = CBProPublic(sandbox_mode=False)
    
    price = cb.asset_price(working_symbol)

    assert type(price) == str
    assert type(float(price)) == float
    assert price == requests.get(f'{base_url}products/{working_symbol.upper()}-USD/ticker').json()['price']

    with pytest.raises(Exception):
        cb.asset_price(unvalid_symbol)
    

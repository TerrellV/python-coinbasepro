from coinbase_pro.public_api import CBProPublic


def test_get_asset_used_price():
    cb = CBProPublic()
    assert type(cb.get_asset_usd_price('BTC')) == str
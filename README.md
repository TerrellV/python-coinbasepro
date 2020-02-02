# Coinbase Pro Python API

An unofficial python package for interacting with the Coinbase Pro API. This package can be used to query both public and user specific exchange data.

## Quick Start - Public

```python
from coinbase_pro import CBProPublic

public_api = CBProPublic()
```

```python
# Bitcoin Price

price = public_api.asset_price('btc')
print(price) # returns most recent price as a string
```

```python
# Available Trading Pairs

trading_pairs = public_api.trading_pairs()
print(trading_pairs)
```

```python
# Historical Prices
# Example: Hourly prices for LTC from 2017-10-01 to 2018-01-01

price_history = public_api.historical_prices(
    product_id='LTC-USD',
    candle_interval='hourly',
    start='2017-10-01',
    end='2018-01-01'
)
print(price_history)
```

## Quick Start - Authenticated

In order to use the authenticated api, you will need to create a file named credentials.json with a secret, passphrase, and api_key. The credentials file should be formatted as follows.

```json
# credentials.json

{
    "secret": "[api secret]",
    "passphrase": "[api passphrase]",
    "api_key": "[api key]"
}
```

Load your credentials file and pass it as a dictionary to the CBProAuthenticated class upon initialization.

> **Warnings**:
>
>1. Never store your api credentials directly in your code
>2. Never commit your credentials.json file to a git repository

```python
from coinbase_pro import CBProAuthenticated

with open('credentials.json') as f:
    credentials = json.loads(f.read())
    auth_api = CBProAuthenticated(credentials)
```

```python
asset_activity = auth_api.asset_activity(
    asset_symbol='BTC',
    start_date='2019-01-01',
    end_date='2020-01-01'
)
print(asset_activity)
```

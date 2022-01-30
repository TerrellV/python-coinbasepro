# python-coinbasepro

An unofficial python package for interacting with the Coinbase Pro API. This package can be used to query both public and authenticated endpoints. This package enables: retrieving live price data, retrieving historical price data, placing market buy and sell orders, depositing fiat, and many other features. See below for examples.

This has been a personal project of mine for some time now. Feel free to test it out and
let me know if you found it useful. Thank you!

> **WARNING**</br>
>Use at your own risk. This project is currently under development.



## Installation

```python
# Install from pypi (most common)
pip install cbp-client
```

```bash
# Install from Github
pip install git+https://github.com/TerrellV/python-coinbasepro.git
```

## Public API Examples

No authentication required
```python
>>> from cbp_client import PublicAPI
>>> api = PublicAPI()
```

### Get current bitcoin price

```python
>>> api.price('btc')
'32615.98'
```

### Get current ETH-BTC price

```python
>>> api.price(base_currency='eth', quote_currency='btc')
'0.03934'
```

### Get historical prices

This method is useful becuase it can return large sets of granular, historical,
price data. In the example below, we requested one year of hourly price data
for LTC-USD. In just 16 seconds 8,639 rows of price data are returned.
`api.historical_prices` returns a generator object. This allows you to loop
through the data without loading the entire response into memory.

```python
>>> price_history = api.historical_prices(
        product_id='LTC-USD',
        candle_interval='hourly',
        start='2017-01-01',
        end='2018-01-01'
    ) # a generator object is returned

>>> list(price_history)
[
    Candle(start='2017-10-01T00:00:00', open='55.26', high='55.33', low='54.86', close='55.26', volume='18231.73237201'),
    Candle(start='2017-10-01T01:00:00', open='55.26', high='55.26', low='54.51', close='54.7', volume='19696.71425587'),
    Candle(start='2017-10-01T02:00:00', open='54.7', high='54.7', low='53.74', close='53.96', volume='20342.70035151'),
    Candle(start='2017-10-01T03:00:00', open='53.93', high='54.45', low='53.74', close='54.4', volume='7261.14770822'),
    Candle(start='2017-10-01T04:00:00', open='54.4', high='54.63', low='54.4', close='54.6', volume='4633.03379232'),
    ...
]
```

### Get all products

```python
>>> api.products()
[
    Product(id='BCH-BTC', display_name='BCH/BTC', base_currency='BCH', quote_currency='BTC', ...),
    Product(id='LINK-ETH', display_name='LINK/ETH', base_currency='LINK', quote_currency='ETH', ...),
    ...
]
```

### Filter products

the products method will filter the returned product list by any attribute specified. To filter, simply specify
the attribute as an argument and set it equal to the value you'd like to filter on. For example,
To retrieve only /USD trading pairs, set quote_currency='USD'. To retrieve only /BTC trading pairs, set quote_currency=BTC.

```python
>>> api.products(quote_currency='USD')
[
    Product(id='BTC-USD', display_name='BTC/USD', base_currency='BTC', quote_currency='USD', ...),
    Product(id='LINK-ETH', display_name='ETH/USD', base_currency='ETH', quote_currency='USD', ...),
    ...
]
```

## Authenticated API

The Authenticated API client provides access to account level details AND all `PublicAPI` methods referenced above. In order to use the live authenticated api, you must provide credentials through one of the following methods: pass a credentials dictionary to the AuthAPI class or set environment variables as shown below.

```python
from cbp_client import AuthAPI
from pathlib import Path
import json

creds = json.loads(Path('credentials.json').read_text())['live']
api = AuthAPI(creds)
```
```json
# credentials.json file loaded in python example above
{
    "live": {
        "secret": "replace_this_with_secret",
        "passphrase": "replace_this_with_passphrase",
        "api_key": "replace_this_with_api_key"
    },
    "sandbox": {
        "secret": "replace_this_with_secret",
        "passphrase": "replace_this_with_passphrase",
        "api_key": "replace_this_with_api_key"
    }
}
```
### Setting Credentials Using Environment Variables
windows cmd.exe example
```shell
set api_key=INSERT_YOUR_INFO
set api_passphrase=INSERT_YOUR_INFO
set api_secret=INSERT_YOUR_INFO
```
bash example
```bash
export api_key=INSERT_YOUR_INFO
export api_passphrase=INSERT_YOUR_INFO
export api_secret=INSERT_YOUR_INFO
```
Sandbox credential example.
If you are setting environment variables for your sandbox environment, prefix the variables names with "sandbox_" as shown.
```shell
set sandbox_api_key=INSERT_YOUR_INFO
set sandbox_api_passphrase=INSERT_YOUR_INFO
set sandbox_api_secret=INSERT_YOUR_INFO
```
> **Warning**:
>1. Never store your api credentials directly in your code
>2. Never commit your credentials.json file to a git repository

### Sandbox Authenticated API

You should test your code before you deploy it. One way to do this without spending real money is
to use the sandbox api. Set `sandbox_mode=True` to instruct the authenticated api client to use the
sandbox api url. Additionally, when connecting with the authenticated sandbox api client,
ensure you are loading your sandbox credentials from your credentials.json file or else it wont work.

```python
from cbp_client import AuthAPI
from pathlib import Path
import json

creds = json.loads(Path('credentials.json').read_text())['sandbox']
api = AuthAPI(creds, sandbox_mode=True)
```

### Get account balance
```python
>>> api.balance('btc')
'0.0000000000000000'
```

### Place a market-buy order
```python
>>> api.market_buy(10, product_id='btc-usd')
<Response [200]>
```

### Place a market-sell order

```python
>>> api.market_buy(size='0.01', product_id='eth-usd')
<Response [200]>
```

### Deposit money into coinbase pro

```python
>>> payment_method = api.payment_methods(name='Focus Financial ******0000')
>>> sandbox_auth_api.deposit(
        amount=10,
        currency='USD',
        payment_method_id=payment_method['id']
    )
<Response [200]>
```

### Get account history

```python
>>> hist = api.account_history(symbol='btc', start_date='2021-01-01') # returns a generator object
>>> for record in hist:
        print(record)
{
    'id': 'activity_id',
    'amount': '-0.0100000000000000',
    'balance': '0',
    'created_at': '----creation date----',
    'type': 'match',
    'details': {
        'order_id': '----order id----',
        'product_id': 'BTC-USD',
        'trade_id': '----trade id----'
    }
}
...
```
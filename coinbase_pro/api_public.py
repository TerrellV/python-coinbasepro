from coinbase_pro.api import API
from coinbase_pro.history import History

from datetime import datetime

class CBProPublic():
    def __init__(self, sandbox_mode=False):
        LIVE_URL = 'https://api.pro.coinbase.com/'
        SANDBOX_URL = 'https://api-public.sandbox.pro.coinbase.com/'

        base_url = SANDBOX_URL if sandbox_mode else LIVE_URL
        self.history = History(base_url)
        self.api = API(base_url)
    
    def usd_price(self, currency):
        '''Get the price in USD for a given asset'''
        endpoint = f'products/{currency.upper()}-USD/ticker'
        price = self.api.get(endpoint).json()['price']
        return price
    
    def exchange_rate(self, currency_pair):
        '''Get the exchange_rate for a given asset'''
        endpoint = f'products/{currency_pair.upper()}/ticker'
        price = self.api.get(endpoint).json()['price']
        return price

    def exchange_time(self):
        '''Return the exchange time in an iso formatted string'''
        endpoint = 'time'
        time_str = self.api.get(endpoint).json()['iso']
        exchange_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')

        return exchange_time.isoformat(sep=' ')
    
    def historical_prices(self, product_id, start=None, end=None, candle_interval='daily', debug=False):
        return self.history.build(product_id, start, end, candle_interval, debug)

    def trading_pairs(self):
        product_info = self.api.get('products').json()

        return [d['id'] for d in product_info]

if __name__ == '__main__':
    cb = CBProPublic()
    print(cb.api.get('fake_endpoint'))
    # h = cb.historical_prices('LTC-USD', candle_interval='hourly', start='2020-01-01', end='2020-02-01', debug=True)
    # print(cb.exchange_rate('eth-BTC'))
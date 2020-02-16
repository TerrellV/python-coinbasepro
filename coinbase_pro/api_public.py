from coinbase_pro.api import API
from coinbase_pro.history import History



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
        '''Return the exchange time in iso format'''
        endpoint = 'time'
        iso_time = self.api.get(endpoint).json()['iso']
        return iso_time
    
    def historical_prices(self, product_id, start=None, end=None, candle_interval='daily', debug=False):
        return self.history.build(product_id, start, end, candle_interval, debug)

    def trading_pairs(self):
        return self.api.get('products').json()

if __name__ == '__main__':
    cb = CBProPublic()
    # h = cb.historical_prices('LTC-USD', candle_interval='hourly', start='2020-01-01', end='2020-02-01', debug=True)
    # print(cb.exchange_rate('eth-BTC'))
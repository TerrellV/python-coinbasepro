from coinbase_pro.api import API
from coinbase_pro.history import History
import time
import json
from datetime import datetime
from decimal import Decimal

class CBProPublic():
    def __init__(self, sandbox_mode=False):
        LIVE_URL = 'https://api.pro.coinbase.com/'
        SANDBOX_URL = 'https://api-public.sandbox.pro.coinbase.com/'

        base_url = SANDBOX_URL if sandbox_mode else LIVE_URL
        self.history = History(base_url)
        self.api = API(base_url)
    

    def twenty_four_hour_stats(self, product_id):
        return self.api.get(f'products/{product_id}/stats').json()

    def usd_market_volume(self):
        '''get min $ volume of __/USD trading pairs in past 24 hrs'''
        usd_trading_pairs = [x for x in self.trading_pairs() if x.split('-')[1] == 'USD']
        
        payload = []

        for pair in usd_trading_pairs:
            stats = self.twenty_four_hour_stats(pair)
            volume = str(round(Decimal(stats['volume']) * Decimal(stats['low']), 2))
            payload.append({'currency_pair': pair, 'usd_volume': volume})
            time.sleep(0.4)
        
        sorted_payload = sorted(payload, key=lambda x: Decimal(x['usd_volume']), reverse=True)

        return sorted_payload
            
    def usd_price(self, currency, delay=False):
        '''Get the price in USD for a given asset'''
        endpoint = f'products/{currency.upper()}-USD/ticker'
        price = self.api.get(endpoint).json()['price']

        if delay:
            time.sleep(0.4)

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
    for x in cb.usd_market_volume():
        volume = Decimal(x['usd_volume'])
        pair = x['currency_pair']
        print(f'{pair} | {volume:,.2f}')

    # h = cb.historical_prices('LTC-USD', candle_interval='hourly', start='2020-01-01', end='2020-02-01', debug=True)
    # print(cb.exchange_rate('eth-BTC'))
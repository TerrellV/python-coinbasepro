# built-in
import time
import json
from datetime import datetime
from decimal import Decimal

# local
from cbp_client.api import API
from cbp_client.history import History


class CBProPublic(API):
    """Retrieves publicly available information from the Coinbase Pro API.

    Usage Example:
        CBProPublic.usd_price('btc') => '10,000'
    
    Arguments:
        sandbox_mode (bool): If true, use sandbox api, if false, use live api

    Attributes:
        history: ....
        
        products (list): Information about available products, also known as trading pairs
            
            Example:
            [{id: 'BTC-USD', quote_currency: 'USD', base_currency: 'BTC' ...}]

        currencies (list): Information about listed currencies

            Example:
            [{id: 'BTC', name: 'Bitcoin', status: 'online' ...}]

        __api: private class to help simplify get and put requests to endpoints
    """

    def __init__(self, sandbox_mode=False):
        
        LIVE_URL = 'https://api.pro.coinbase.com/'
        SANDBOX_URL = 'https://api-public.sandbox.pro.coinbase.com/'
        
        self.base_url = SANDBOX_URL if sandbox_mode else LIVE_URL
        
        super().__init__(base_url=self.base_url)

        self.history = History(self.base_url)

        self.products = self.get('products').json()
        self.currencies = self.get('currencies').json()

    def twenty_four_hour_stats(self, product_id):
        """Provides 24/hr stats for a specific asset.

        Example product_id: 'btc-usd'
        """

        return self.get(f'products/{product_id}/stats').json()

    def usd_market_volume(self):
        """Returns min $ volume of USD trading pairs over past 24 hrs."""

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
        '''Returns the latest price in USD for a given asset'''
        endpoint = f'products/{currency.upper()}-USD/ticker'
        price = self.get(endpoint).json()['price']

        if delay:
            time.sleep(0.4)

        return price
    
    def exchange_rate(self, product_id):
        """Returns the most recent exchange_rate for a given crypto asset.

        Arguments:
        product_id (str): a currency pair seperated by -. For example 'btc-usd'  
        
        """
        endpoint = f'products/{product_id.upper()}/ticker'
        price = self.get(endpoint).json()['price']
        return price

    def exchange_time(self):
        '''Returns the current exchange time as an iso formatted string'''
        endpoint = 'time'
        time_str = self.get(endpoint).json()['iso']
        exchange_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')

        return exchange_time.isoformat(sep=' ')
    
    def historical_prices(self, product_id, start=None, end=None, candle_interval='daily', debug=False):
        return self.history(product_id, start, end, candle_interval, debug)

    def trading_pairs(self):
        """Returns a list of available trading pairs as product-ids.
        
            Sample product-id: 'btc-usd'
        """
        product_info = self.get('products').json()

        return [d['id'] for d in product_info]

if __name__ == '__main__':
    cb = CBProPublic()
    for x in cb.usd_market_volume():
        volume = Decimal(x['usd_volume'])
        pair = x['currency_pair']
        print(f'{pair} | {volume:,.2f}')

    # h = cb.historical_prices('LTC-USD', candle_interval='hourly', start='2020-01-01', end='2020-02-01', debug=True)
    # print(cb.exchange_rate('eth-BTC'))
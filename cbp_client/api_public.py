"""Class for accessing public coinbase pro endpoints"""


# built-in
import time
from datetime import datetime
from decimal import Decimal
from typing import List
from collections import namedtuple

# local
from cbp_client.api import API
from cbp_client.history import history



Product = namedtuple('Product', ['base', 'quote'])


class CBProPublic(API):
    """
    Retrieve publicly available information from the Coinbase Pro API.

    Example
    -------
    >>>CBProPublic.usd_price('btc')
    '10,000'
    
    Arguments
    ---------
    sandbox_mode : bool
        If true, use sandbox api, if false, use live api.

    Attributes
    ----------
        history: ....
        
        products : list
            Information about available products, also known as trading pairs.
            
            Example:
            [{id: 'BTC-USD', quote_currency: 'USD', base_currency: 'BTC' ...}]

        currencies : list
            Information about listed currencies.

            Example:
            [{id: 'BTC', name: 'Bitcoin', status: 'online' ...}]

        __api : cls
            Private class to help simplify get and put requests to endpoints.
    """

    LIVE_URL = 'https://api.pro.coinbase.com/'
    SANDBOX_URL = 'https://api-public.sandbox.pro.coinbase.com/'

    def __init__(self, sandbox_mode=False):
        
        self.base_url = (
            CBProPublic.SANDBOX_URL
            if sandbox_mode
            else CBProPublic.LIVE_URL
        )
        
        super().__init__(base_url=self.base_url)

        # self.history = History(self.base_url)

        self._products = self.get('products').json()
        self._currencies = self.get('currencies').json()

    def twenty_four_hour_stats(self, product_id: str) -> dict:
        """
        Provides 24/hr stats for a specific asset.

        Volume is in base currency units. open, high, low are in quote
        currency units.

        Endpoint
        --------
        /products/{product_id}/stats endpoint

        Example
        -------
        >>> CBProPublic.twenty_four_hour_stats('btc-usd')
        {
            "open": "6745.61000000", 
            "high": "7292.11000000", 
            "low": "6650.00000000", 
            "volume": "26185.51325269", 
            "last": "6813.19000000", 
            "volume_30day": "1019451.11188405"
        }

        Returns
        -------
        dict
        """
        return self.get(f'products/{product_id}/stats').json()

    def _get_trading_pairs(
            self,
            symbols: List[str, ...],
            usd_only: bool=True
        ) -> list:
        pass
        # usd_pairs = [
        #     x
        #     for x in self.trading_pairs
        #     if x.split('-')[1] == 'USD'
        # ]

        # if usd_only:
        #     return [p for p in usd_pairs if p.split('-')[]]

    def usd_market_volume(self, symbols: List[str, ...]) -> list:
        """Return 24 hour volumes for given product-ids."""

        all_usd_pairs = [
            x
            for x in self.trading_pairs()
            if x.split('-')[1] == 'USD'
        ]
        filtered_pairs = [
            x
            for x in all_usd_pairs
            if x.split('-')[0] in symbols
        ]
        payload = []

        for pair in usd_trading_pairs:
            stats = self.twenty_four_hour_stats(pair)
            volume = str(round(Decimal(stats['volume']) * Decimal(stats['low']), 2))
            payload.append({'currency_pair': pair, 'usd_volume': volume})
            time.sleep(0.4)
        
        sorted_payload = sorted(payload, key=lambda x: Decimal(x['usd_volume']), reverse=True)

        return sorted_payload
            
    def usd_price(self, currency: str, delay: bool=False) -> str:
        '''Returns the latest price in USD for a given asset'''
        endpoint = f'products/{currency.upper()}-USD/ticker'
        price = self.get(endpoint).json()['price']
        if delay: time.sleep(0.4)
        return price
    
    def exchange_rate(self, product_id: str) -> str:
        """Returns the most recent exchange_rate for a given crypto asset.

        Arguments
        ---------
        product_id : str
            A currency pair seperated by -. For example 'btc-usd'  
        """
        endpoint = f'products/{product_id.upper()}/ticker'
        return self.get(endpoint).json()['price']

    def exchange_time(self):
        """Returns the current exchange time as an iso formatted string"""
        time_str = self.get('time').json()['iso']
        exchange_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')

        return exchange_time.isoformat(sep=' ')
    
    def historical_prices(self,
            product_id,
            start=None,
            end=None,
            candle_interval='daily',
            debug=False
        ) -> pd.Dataframe:
        return self.history(product_id, start, end, candle_interval, debug)

    @property
    def products(self):
        return self._products

    @property
    def currencies(self):
        return self._currencies

    @property
    def usd_trading_pairs(self):
        """Return USD trading pairs"""
        return [p for p in self.trading_pairs if p.quote.lower() == 'usd']

    @property
    def trading_pairs(self):
        """Returns a list of available trading pairs as product-ids.
        
            Sample product-id: 'btc-usd'
        """
        split_ids = [d['id'].split('-') for d in self.products]
        return [Product(base, quote) for base, quote in split_ids]

"""Class for accessing public coinbase pro endpoints"""


from datetime import datetime
from typing import List

from cbp_client.product import Product, is_fully_tradeable, is_live
from cbp_client.api import API
from cbp_client.history import History, Interval


class PublicAPI(API):
    """
    Retrieve publicly available information from the Coinbase Pro API.

    Example
    -------
    >>>cb = PublicAPI()
    >>>cb.price('btc')
    '10,000'

    Arguments
    ---------
    sandbox_mode : bool
        If true, use sandbox api, if false, use live api. Default = False

    Attributes
    ----------
    products : list
        Information about available products, also known as trading pairs.

        Example:
        [{id: 'BTC-USD', quote_currency: 'USD', base_currency: 'BTC' ...}]

    currencies : list
        Information about listed currencies.

        Example:
        [{id: 'BTC', name: 'Bitcoin', status: 'online' ...}]
    """

    def __init__(self, sandbox_mode=False):

        self.api = API(sandbox_mode)
        self.History = History
        self._products = list(self._decorated_products())
        self.currencies = self.get('currencies').json()

    def get(self, endpoint):
        return self.api.get(endpoint)

    def twenty_four_hour_stats(self, product_id: str) -> dict:
        """
        Provides 24/hr stats for a specific asset.

        Defaults to USD trading pair unless specified. Volume is in base
        currency units. open, high, low are in quote currency units.

        Endpoint
        --------
        /products/{product_id}/stats endpoint

        Example
        -------
        >>> PublicAPI.twenty_four_hour_stats('btc')
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

    def price(self, base_currency: str, quote_currency='USD') -> str:
        '''
        Returns the latest price for a given asset.

        By default, this method will seek a price using a USD trading pair. If
        one does not exist, it will fail. If you'd like to price an asset
        against a crypto asset, adjust the quote currency. For example
        if you wanted to know "how much bitcoin can I get for one etherium?",
        set base_currency='eth' and quote_currency='btc'.

        Parameters
        ----------
        base_currency : str
            The first symbol in a trading pair / product id. The currency you
            are interested in getting a price for.
        quote_currency : str
            The second symbol in a trading pair / product id. The currency you
            wish to price the base currency in. Default = USD
        '''
        base = base_currency.upper()
        quote = quote_currency.upper()
        endpoint = f'products/{base}-{quote}/ticker'
        price = self.get(endpoint).json()['price']
        return price

    def exchange_time(self):
        """Returns the current exchange time as an ISO formatted string"""
        time_str = self.get('time').json()['iso']
        exchange_time = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S.%fZ')

        return exchange_time.isoformat(sep=' ')

    def historical_prices(
            self,
            product_id: str,
            start=None,
            end=None,
            candle_interval: str = Interval.DAILY.name) -> List[History.Candle]:
        """
        Get historical data for a specifc product / trading pair.

        This method is great for requesting large sets of historical data at
        fine granularities. For example, one could request two years of
        hourly or even minute candle data. Note, the coinbase api only returns
        a max of 300 items per request. For that reason, longer timelines
        with finer granularity might take some time to complete. A slight
        delay has been built into this module for requests larger than 300
        candles to ensure rate limits are respected.

        Parameters
        ----------
        product_id : str
            Product Identifier. For example 'ETH-BTC'
        start : str
            ISO formatted string representing the start datetime.
        end : str, Optional
            ISO formatted string representing the end datetime. Defaults to
            now.
        candle_interval : str, Optional
            Length of each candle to be returned. To get daily data, set
            candle_interval='daily'. Possible values: minute, five_minute,
            fifteen_minute, hourly, six_hour, daily. Defaults to daily.

        Returns
        -------
        generator
            The returned object is a generator, meaning it wont run until you
            begin iterating over it. It will only

        """
        return self.History(
            start=start,
            end=end,
            product_id=product_id.upper(),
            interval=candle_interval,
            api=self.api
        )()

    def products(self, **keyword_args) -> List[Product]:
        """
        Filters for a list of products. Default return all.

        A product is a trading pair offered on the exchange.
        By default, all products offered by coinbase pro are returned. To
        filter the results, pass in an a keyword=value pair to filter on.

        Parameters
        ----------
        live_only : bool
            Filters for only "live" trading pairs.
            A pair is considered "live" when:
                status='online'

        fully_tradeable : bool
            Filters for fully tradeable pairs. A trading pair is considered
            "fully_tradeable" when:
                status='online'
                cancel_only=False
                limit_only=False
                post_only=False
                trading_disabled=False

        **keyword_args
            Additionally, one can filter on any key returned by the products
            endpoint. See the api docs for more info.
            https://docs.pro.coinbase.com/#products

        Example
        -------
        Get all products:
        >>> PublicApi().products()

        Filters for fully_tradeable products:
        >>> PublicApi().products(fully_tradeable=True)

        Filters for products quoted in USD
        >>> PublicApi().products(quote='USD')

        Filters for specific product
        >>> PublicApi().products(id='BTC-USD')

        Returns
        -------
        list
            [Product('BTC-USD'), Product('ETH-USD'), ...]
        """

        def _should_include(product, keyword_args):
            """Check if attributes with provided values exists on product"""
            for keyword, value in keyword_args.items():
                keyword = keyword.lower()
                attribute_value = getattr(product, keyword, not value)

                try:
                    if str(attribute_value).upper() != str(value).upper():
                        return False
                except AttributeError:
                    if attribute_value != value:
                        return False

            return True

        return [product
                for product in self._products
                if _should_include(product, keyword_args)]

    def _decorated_products(self):
        """Returns products with additional attributes.
        Adds full_tradeable and is_live attributes to each product.
        """
        for product in self.get('products').json():
            yield Product(
                **product,
                live=is_live(product),
                fully_tradeable=is_fully_tradeable(product)
            )

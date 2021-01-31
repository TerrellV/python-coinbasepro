import time

from cbp_client.auth import Auth
from cbp_client.api_public import PublicAPI
from collections import namedtuple
from typing import Union, List
from datetime import datetime
from types import GeneratorType


Account = namedtuple('Account', ['id',
                                 'currency',
                                 'balance',
                                 'available',
                                 'hold',
                                 'profile_id',
                                 'trading_enabled'])


class AuthAPI(PublicAPI):

    def __init__(self, credentials, sandbox_mode=False):
        super().__init__(sandbox_mode)

        self.auth = Auth(**credentials)
        self._accounts = []
        self.refresh_accounts()

    def accounts(self, currency: str = None) -> Union[List[Account], Account]:

        if currency is None:
            return self._accounts

        for account in self._accounts:
            if account.currency.lower() == currency.lower():
                return account

    def balance(self, symbol: str) -> str:
        '''Returns balance for specific currency in coinbase pro'''
        return self.accounts(currency=symbol.lower()).balance

    def refresh_accounts(self):
        self._accounts = [
            Account(**act)
            for act in self.api.get('accounts', auth=self.auth).json()
        ]

    def fill_history(
        self,
        product_id: str,
        order_id=None,
        start_date=None,
        end_date=None
    ):
        '''Get all fills associated with a given product id'''
        end_point = 'fills'
        params = {'product_id': product_id.upper()}
        data = self.api.get_paginated_endpoint(
            end_point,
            params=params,
            start_date=start_date,
            date_field='created_at',
            auth=self.auth
        )

        return data if data is not None else []

    def account_history(self, symbol, start_date, end_date=None) -> GeneratorType:
        '''Get all activity related to a given asset'''
        account_id = self.accounts(currency=symbol).id
        endpoint = f'accounts/{account_id}/ledger'
        end_date = datetime.now().isoformat() if end_date is None else end_date

        return self.api.get_paginated_endpoint(
            endpoint=endpoint,
            auth=self.auth,
            start_date=start_date
        )

    def filled_orders(self, product_id=None):
        orders = self.api.get_paginated_endpoint(
            endpoint='orders',
            date_field='done_at',
            start_date='2019-01-01',
            auth=self.auth,
            params={'status': 'done'}
        )

        return [
            o for o in orders
            if o.get('done_reason', '').lower() == 'filled'
        ]

    def market_buy(self, funds, product_id, delay=False):
        '''Market buy as much crypto as specified funds allow
        Parameters
        ----------
        funds : str
            The amount of fiat currency to purchase crypto with. Example, if
            funds=50 and product_id=BTC-USD then you will purchase $50 worth of
            crypto. Fees will be taken out of the specified funds amount.
        product_id : str
        delay : bool, Optional
        '''

        order_payload = {
            'side': 'buy',
            'type': 'market',
            'product_id': product_id.upper(),
            'funds': str(funds),
        }

        r = self.api.post(
            endpoint='orders',
            params={},
            data=order_payload,
            auth=self.auth
        )

        if delay:
            time.sleep(0.4)

        return r

    def market_sell(self, size, product_id, delay=False):
        '''Market sell specified quantity of crypto.

        Parameters
        ----------
        size : str
            The quantity of the specified crypto to sell. Example, if
            size=0.1 and product_id=BTC-USD then this will sell 0.1 btc for
            USD. The amount of the quote currency you will receive depends on
            current fees.
        product_id : str
        delay : bool, Optional
        '''

        order_payload = {
            'side': 'sell',
            'type': 'market',
            'product_id': product_id.upper(),
            'size': str(size),
        }

        r = self.api.post(
            endpoint='orders',
            params={},
            data=order_payload,
            auth=self.auth
        )

        if delay:
            time.sleep(0.4)

        return r

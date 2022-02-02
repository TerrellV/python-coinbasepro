import time
from datetime import datetime
from typing import Union, List
from types import GeneratorType
from collections import namedtuple
from cbp_client.helpers import load_credentials

from cbp_client.auth import Auth
from cbp_client.api_public import PublicAPI

Account = namedtuple('Account', ['id',
                                 'currency',
                                 'balance',
                                 'available',
                                 'hold',
                                 'profile_id',
                                 'trading_enabled'])


class AuthAPI(PublicAPI):

    def __init__(self, credentials=None, sandbox_mode=False):
        super().__init__(sandbox_mode)

        if credentials is None:
            credentials = load_credentials(sandbox_mode)

        self.auth = Auth(**credentials)
        self._accounts = []
        self.refresh_accounts()
        self._this_profile_id = self._accounts[0].profile_id

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

    def orders(
        self,
        start_date: str,
        end_date: str = None,
        status: str = None,
        settled: bool = None
    ):
        '''Get orders related to the authenticated account.

        Parameters
        ----------
        start_date: str
            The beginning of the period to retrieve orders from
        end_Date: str
            The end of the period to retrieve orders from. Defaults to now.
        status: str, optional
            When specified, this will filter the list of orders to only those
            with this status.
        settled: bool, optional
            If true, returns only orders where: order['settled']=True
        '''
        end_date = datetime.now().isoformat() if end_date is None else end_date

        no_filters = status is None and settled is None
        status_specified = status is not None

        def _get_orders(params, date_field='created_at'):
            orders = self.api.get_paginated_endpoint(
                endpoint='orders',
                auth=self.auth,
                start_date=start_date,
                params=params
            )
            return [
                o for o in orders
                if o[date_field] >= start_date <= end_date
            ]

        if no_filters:
            orders = _get_orders({'status': 'all'})

        elif settled:
            orders = _get_orders({'status': 'done'})
            orders = [o for o in orders if o['settled']]

        elif status_specified:
            orders = _get_orders({'status': status})

        return orders

    def account_history(
        self,
        symbol: str,
        start_date: str,
        end_date=None
    ) -> GeneratorType:
        '''Get all activity related to a given asset'''
        account_id = self.accounts(currency=symbol).id
        endpoint = f'accounts/{account_id}/ledger'
        end_date = datetime.now().isoformat() if end_date is None else end_date

        return self.api.get_paginated_endpoint(
            endpoint=endpoint,
            auth=self.auth,
            start_date=start_date
        )

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

    def payment_methods(self, name: str = None):
        '''Get list of payment methods'''
        payment_methods = self.api.get(
            endpoint='payment-methods',
            auth=self.auth
        ).json()

        if name is None:
            return payment_methods

        for method in payment_methods:
            if method['name'].lower() == name.lower():
                return method

    def deposit(
        self,
        amount: str,
        payment_method_id: str,
        currency: str = 'USD'
    ):
        return self.api.post(
            endpoint='deposits/payment-method',
            auth=self.auth,
            data={
                'amount': amount,
                'currency': currency,
                'payment_method_id': payment_method_id
            }
        )

    @property
    def profile(self):
        r = self.api.get(f'profiles/{self._this_profile_id}', auth=self.auth)
        profile = r.json()
        return profile

    def get_profiles(self):
        r = self.api.get(f'profiles', auth=self.auth)
        return r.json()

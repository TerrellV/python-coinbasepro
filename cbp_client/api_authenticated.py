import time

from cbp_client.auth import Auth
from cbp_client.api_public import PublicAPI
from collections import namedtuple


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
        self.accounts = []
        self.refresh_accounts()

    def balance(self, symbol: str) -> str:
        '''Returns balance for specific currency in coinbase pro'''
        symbol = symbol.lower()

        for acct in self.accounts:
            if acct.currency.lower() == symbol:
                return acct.balance

    def refresh_accounts(self):
        self.accounts = [
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

    @staticmethod
    def _apply_unique_id_to_activity(entry):
        if entry['type'] == 'match':
            entry['unique_id'] = entry['details.order_id']
            entry['unique_id_type'] = 'order_id'

        if entry['type'] == 'transfer':
            entry['unique_id'] = entry['details.transfer_id']
            entry['unique_id_type'] = 'transfer_id'

        return entry

    def asset_activity(self, asset_symbol, start_date=None, end_date=None):
        '''Get all activity related to a given asset'''

        asset_symbol = asset_symbol.upper()
        account_id = [account['id'] for account in self.accounts if account['currency'] == asset_symbol][0]
        activity = self.api.handle_page_nation(f"accounts/{account_id}/ledger", start_date=start_date, auth=self.auth)
        no_activity = len(activity) == 0

        if no_activity:
            return activity

        activity = map(self._apply_unique_id_to_activity, activity)

        activity = [
            {
                **entry,
                'created_at': entry['created_at'].strftime('%Y-%m-%d %H:%M:%S:%f'),
                'symbol': asset_symbol,
                'amount': str(entry['amount']),
                'balance': str(entry['balance'])
            }
            for entry in activity
        ]

        return activity

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

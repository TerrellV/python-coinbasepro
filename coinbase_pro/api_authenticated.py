import numpy as np
import pandas as pd

import json

from coinbase_pro.auth import Auth
from coinbase_pro.api_public import CBProPublic
from coinbase_pro.api import API

pd.set_option('max_rows', 100)
pd.set_option('max_columns', 15)
pd.set_option('display.width', 500)

class CBProAuthenticated():

    def __init__(self, credentials, sandbox_mode=False):

        LIVE_URL = 'https://api.pro.coinbase.com/'
        SANDBOX_URL = 'https://api-public.sandbox.pro.coinbase.com/'

        base_url = SANDBOX_URL if sandbox_mode else LIVE_URL

        self.cb_public = CBProPublic()
        self.api = API(base_url)
        self.auth = Auth(**credentials)
        self.accounts = self.api.get('accounts', auth=self.auth).json()
    
    def __getattr__(self, name):
        try:
            return getattr(self.cb_public, name)
        except AttributeError:
            raise AttributeError(f'The authenticated and public api objects not not have attribute {name}.')

    def fill_history(self, product_id, order_id=None, start_date=None, end_date=None):
        '''Get all fills associated with a given product id'''
        end_point = 'fills'
        params = {'product_id': product_id.upper()}
        data = self.api.handle_page_nation(end_point, params=params, start_date=start_date, auth=self.auth)
        returned_value = data.copy().to_dict(orient='records')
        return returned_value if data is not None else None
    
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

    def completed_orders(self, product_id=None):
        orders = self.api.handle_page_nation(
            'orders',
            date_field='done_at',
            start_date='2019-01-01',
            auth=self.auth,
            params={'status':'done'}
        )

        orders = list(filter(lambda order: order['done_reason'] == 'filled', orders))

        return orders

if __name__ == '__main__':
    with open('credentials.json') as f:
        credentials = json.loads(f.read())
        auth_api = CBProAuthenticated(credentials)
    
    orders = auth_api.completed_orders()

    print(json.dumps(orders, indent=4))
    

    # asset_activity = auth_api.asset_activity(
    #     asset_symbol='BTC',
    #     start_date='2019-01-01',
    #     end_date='2020-01-01'
    # )

    # print(json.dumps(asset_activity, indent=4))
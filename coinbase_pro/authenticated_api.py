import numpy as np
import pandas as pd

from coinbase_pro.auth import Auth
from coinbase_pro.public_api import CBProPublic
from coinbase_pro.api import API


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

    def get_fill_history(self, product_id, order_id=None, start_date=None, end_date=None):
        end_point = 'fills'
        params = {'product_id': product_id.upper()}
        data = self.api.handle_page_nation(end_point, params=params, start_date=start_date, auth=self.auth)
        returned_value = data.copy().to_dict(orient='records')
        return returned_value if data is not None else None
    
    def get_asset_activity(self, asset_symbol, start_date=None, end_date=None):
        asset_symbol = asset_symbol.upper()
        account_id = [account['id'] for account in self.accounts if account['currency'] == asset_symbol][0]
        df = self.api.handle_page_nation(f"accounts/{account_id}/ledger", start_date=start_date, auth=self.auth)

        if df is None or df.size == 0:
            return None

        df = df.copy()

        if 'details.transfer_id' not in df.columns:
            df['details.transfer_id'] = np.nan

        df['unique_id'] = np.where(df['details.order_id'].notnull(), df['details.order_id'], df['details.transfer_id'])
        df['account_currency'] = asset_symbol
        df['balance'] = pd.to_numeric(df['balance'])
        df['amount'] = pd.to_numeric(df['amount'])
        
        # reset index, sort, and group related entries, then reset index again
        df = df.reset_index()
        df = df.sort_values('created_at', ascending=True)
        df = df.groupby(['unique_id', 'account_currency', 'type']).agg({'created_at': 'last', 'amount': 'sum', 'balance': 'last', 'details.product_id': 'last'})
        df = df.reset_index().set_index('created_at').sort_values('created_at', ascending=True)

        # add column to dataframe
        df['entry_type'] = np.where(df['amount'] > 0, 'debit', 'credit')
        
        transaction_slice = df[start_date:end_date].reset_index().copy().to_dict(orient='records')

        return transaction_slice
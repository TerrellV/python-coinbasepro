import json, time
from decimal import Decimal

import pandas as pd
import numpy as np
import requests
from auth import Auth


class API():
    def __init__(self, base_url):
        self.base_url = base_url
    
    @staticmethod
    def _handle_error(r):
        if r.status_code != 200:
            raise Exception(f'Api Error: Status Code {r.status_code}. Text: {r.text}')

    def get(self, endpoint, params={}, auth=None):
        url = f'{self.base_url}{endpoint}'
        r = requests.get(url=url, auth=auth, params=params)

        self._handle_error(r)

        return r

    def post(self, endpoint, params={}, data={}, auth=None):
        url = f'{self.base_url}{endpoint}'
        data = json.dumps(data)
        r = requests.post(url=url, auth=auth, params=params, data=data)

        self._handle_error(r)
        
        return r

    def handle_page_nation(self, endpoint, start_date, params={}, auth=None):
        all_results = []

        def make_request(after=None):
            response = self.get(endpoint, params={**params, 'after':after}, auth=auth)

            beginning_cursor = response.headers.get('cb-before', None) # start of page index; used for newer results
            end_cursor = response.headers.get('cb-after', None) # end of page index; used for older results

            data = response.json()

            number_of_results = len(data)

            if number_of_results == 0:
                # no data available in this page (request)
                return

            # flatten data; 
            df = pd.io.json.json_normalize(data, sep='.')
            df['created_at'] = pd.to_datetime(df['created_at'])
            df = df.set_index('created_at')
            df = df.sort_values('created_at', ascending=False)

            all_results.append(df)
            earliest_date_in_results = df[-1:].index # last value

            if earliest_date_in_results < start_date:
                return # no need to request additional data
            else:
                rand_int_below_ten = Decimal(str(np.random.randint(11)))
                wait_time = rand_int_below_ten / Decimal('10')
                time.sleep(float(wait_time))
                make_request(after=end_cursor)


        make_request()

        if len(all_results) > 0:
            all_results = pd.concat(all_results, sort=True).sort_values('created_at', ascending='True')
            return all_results[start_date:]
        else:
            return None



class CBProPublic():
    def __init__(self, sandbox_mode=False):
        LIVE_URL = 'https://api.pro.coinbase.com/'
        SANDBOX_URL = 'https://api-public.sandbox.pro.coinbase.com/'

        base_url = SANDBOX_URL if sandbox_mode else LIVE_URL

        self.api = API(base_url)
    
    def get_asset_usd_price(self, currency):
        endpoint = f'products/{currency.upper()}-USD/ticker'
        price = self.api.get(endpoint).json()['price']
        return price


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
        

if __name__ == '__main__':
    with open('creds.json') as f:
        creds = json.loads(f.read())
        cb = CBProPublic()
        print(cb.get_asset_usd_price('BTC'))
import json, time
from decimal import Decimal

import pandas as pd
import numpy as np
import requests


class API():
    def __init__(self, base_url):
        self.base_url = base_url
    
    @staticmethod
    def _handle_error(r):
        if r.status_code != 200:
            error_message = json.loads(r.text)['message']
            raise Exception(f'Api Error: Status Code {r.status_code}\n\nError Message: {error_message}\n')
    
    @staticmethod
    def _random_float_between_zero_one():
        rand_int_below_ten = Decimal(str(np.random.randint(11)))
        return float(rand_int_below_ten / Decimal('10'))

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

    def handle_page_nation(self, endpoint, start_date, date_field='created_at', params={}, auth=None):
        all_results = []

        def make_request(after=None):
            response = self.get(endpoint, params={**params, 'after':after}, auth=auth)
            end_cursor = response.headers.get('cb-after', None) # end of page index; used for older results
            data = response.json()
            number_of_results = len(data)

            if number_of_results == 0:
                # no data available in this page (request)
                return

            # flatten data; 
            df = pd.json_normalize(data, sep='.')
            df[date_field] = pd.to_datetime(df[date_field])
            df = df.set_index(date_field)
            df = df.sort_values(date_field, ascending=False)

            all_results.append(df)
            earliest_date_in_results = df[-1:].index # last value

            if earliest_date_in_results < start_date:
                return # no need to request additional data
            else:
                time.sleep(self._random_float_between_zero_one())
                make_request(after=end_cursor)

        make_request()

        if len(all_results) > 0:
            all_results = pd.concat(all_results, sort=True).sort_values(date_field, ascending='True')
            df = all_results[start_date:].copy().reset_index()
            # print(type(df[date_field].dtypes))
            df[date_field] = df[date_field].dt.strftime('%Y-%m-%d %H:%M:%S:%f')
            return df.to_dict(orient='records')
        else:
            return []
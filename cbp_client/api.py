import json, time, re, inspect
from decimal import Decimal

import pandas as pd
import numpy as np
import requests

from cbp_client.pagination import GetPaginatedEndpoint

# local helper functions
def _random_float_between_zero_one():
    rand_int_below_ten = Decimal(str(np.random.randint(11)))
    return float(rand_int_below_ten / Decimal('10'))

def _http_error_message(e, r):
    response_text = json.loads(r.text)['message']
    return inspect.cleandoc(f"""
        Requests HTTP error: {e}
            Url: {r.url}
            Status Code: {r.status_code}
            Response Text: {response_text}
            Note: Check the url and endpoint
    """)

class API:
    def __init__(self, base_url):
        self.base_url = re.sub('\/*$', '', base_url) # remove trailing slash

    def _build_url(self, endpoint):
        endpoint = re.sub('^\/*', '', endpoint) # remove leading slash
        endpoint = re.sub('\/*$', '', endpoint) # remove trailing slash
        return f'{self.base_url}/{endpoint}'
    
    @staticmethod
    def _http_post(url, params={}, data={}, auth=None):
        data = json.dumps(data)
        
        try:
            r = requests.post(url=url, auth=auth, params=params, data=data)
            r.raise_for_status()
        except requests.HTTPError as e:
            raise requests.HTTPError(_http_error_message(e, r))
        except requests.ConnectTimeout as e:
            raise e
        except requests.ConnectionError as e:
            raise e
        else:
            return r

    @staticmethod
    def _http_get(url, params={}, auth=None):
        try:
            r = requests.get(url=url, auth=auth, params=params)
            r.raise_for_status()
        except requests.ConnectionError as e:
            raise e
        except requests.HTTPError as e:
            raise requests.HTTPError(_http_error_message(e, r))
        else:
            return r
    
    def get(self, endpoint, params={}, auth=None):
        return self._http_get(self._build_url(endpoint), params=params, auth=auth)
    
    def post(self, endpoint, params, auth, data={}):
        return self._http_post(url=self._build_url(endpoint), data={}, params=params, auth=auth)
    
    def get_paginated_endpoint(self, endpoint, start_date, date_field='created_at', params={}, auth=None):
        paginated_endpoint = GetPaginatedEndpoint(
            url=self._build_url(endpoint),
            start_date=start_date,
            date_field=date_field,
            params=params,
            auth=auth,
            get_method=self._http_get
        )
        return paginated_endpoint()
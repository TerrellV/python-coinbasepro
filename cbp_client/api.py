"""Base API class for making http requests"""

import json
import re
import inspect
import requests
from cbp_client.auth import Auth
from cbp_client.pagination import handle_pagination


def _http_error_message(e, r):
    response_text = json.loads(r.text)['message']
    return inspect.cleandoc(f"""
        Requests HTTP error: {e}
            Url: {r.url}
            Status Code: {r.status_code}
            Response Text: {response_text}
            Note: Check the url and endpoint
    """)


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


class API:

    LIVE_URL = 'https://api.exchange.coinbase.com'
    SANDBOX_URL = 'https://api-public.sandbox.exchange.coinbase.com'

    def __init__(self, sandbox_mode: bool):
        self.base_url = API.LIVE_URL if not sandbox_mode else self.SANDBOX_URL

    def _build_url(self, endpoint):
        """Constructs full url needed for querying api."""
        endpoint = re.sub(r'^\/*', '', endpoint)  # remove leading slash
        endpoint = re.sub(r'\/*$', '', endpoint)  # remove trailing slash
        return f'{self.base_url}/{endpoint}'

    def get(self, endpoint, params={}, auth=None):
        return _http_get(self._build_url(endpoint), params=params, auth=auth)

    def post(self, endpoint, auth, params={}, data={}):
        return _http_post(
            url=self._build_url(endpoint),
            params=params,
            data=data,
            auth=auth
        )

    def get_paginated_endpoint(
        self,
        endpoint: str,
        start_date: str,
        auth: Auth,
        date_field: str = 'created_at',
        params: dict = {}
    ):
        '''Get paginated endpoint. See documentation in handle_pagination

        Parameters
        ----------
        endpoint : str
            The API endpoint of interest. Example 'products'
        start_date : str
        date_field : str
        params: dict
        auth: Auth
        '''
        return handle_pagination(
            url=self._build_url(endpoint),
            start_date=start_date,
            date_field=date_field,
            params=params,
            auth=auth,
            get_method=_http_get
        )

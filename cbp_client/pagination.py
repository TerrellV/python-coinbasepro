import pandas as pd


class GetPaginatedEndpoint():
    """Help manage paginated coinbase pro endpoints

    Attributes:
        start_date (str):
        url (str):
        params (dict):
        auth (dict):

    Example usage:
        pe = __GetPaginatedEndpoint()
        data = pe.walk_pages()
    """

    def __init__(self, start_date, date_field, url, params, auth, get_method):

        self.url = url
        self.auth = auth
        self.params = params
        self.get = get_method
        self.page = {
            'end_cursor': None,
            'length': None,
            'data': None
        }
        self.start_date = start_date
        self.date_field = date_field
        self.walk_active = True
        self.results = []

    def __call__(self):
        self._walk_pages()

    def _walk_pages(self):
        while self.walk_active:

            self._get_page()

            # if no results are returned, stop!
            if self.page['length'] == 0:
                return  # stop

            df = self._transform_page_response(self.page['data'])
            self.results = self.results.append(df)

            # if earliest date in results comes before our start date then
            # we've gone far enough back in history
            if df[-1:].index < self.start_date:
                self.walk_active = False

    def _get_page(self):
        params = {**self.params, 'after': self.page['end_cursor']}

        r = self.get(self.url, params, self.auth)

        self.page['end_cursor'] = r.headers.get('cb-after', None)
        self.page['data'] = r.json()
        self.page['length'] = len(self.page['data'])

    def _transform_page_response(self, data):
        df = pd.json_normalize(data, sep='.')
        df[self.date_field] = pd.to_datetime(df[self.date_field])

        return (df.set_index(self.date_field)
                .sort_values(self.date_field, ascending=False))

    def _transform_all_results(self):
        self.results = (
            pd.concat(self.results, sort=True)
            .sort_values(self.date_field, ascending='True')
        )

        df = self.results[self.start_date:].copy().reset_index()

        df[self.date_field] = (
            df[self.date_field].dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        )
        return df.to_dict(orient='records')

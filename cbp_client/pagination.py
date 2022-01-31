'''Class for handling paginated endpoints'''
from datetime import datetime
from cbp_client.auth import Auth
import time


COINBASE_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'


def handle_pagination(
    start_date: str,
    date_field: str,
    url: str,
    params: dict,
    auth: Auth,
    get_method
):
    """Help manage paginated coinbase pro endpoints

    Parameters:
        start_date : str
        date_field : str
            Datefield to use for pagination
        url : str
        params : dict
        auth : Auth
        get_method : func
            Function used to call coinbase api. Should return response obj
            and take in params, url, and auth.

    Example usage:
        pe = GetPaginatedEndpoint()
        data = pe.walk_pages()
    """

    # assumes all paginated endpoints require valid auth
    if not isinstance(auth, Auth):
        raise ValueError(f'Invalid Auth argument: {auth}')

    end_cursor = None
    start_date = datetime.fromisoformat(start_date)

    while True:

        params = {**params, 'after': end_cursor}
        r = get_method(url, params, auth=auth)
        end_cursor = r.headers.get('cb-after', None)
        page = r.json()

        if len(page) == 0:
            break

        yield from page

        earliest_date = min(row[date_field] for row in page)
        earliest_date = datetime.strptime(earliest_date, COINBASE_DATE_FORMAT)

        if earliest_date <= start_date:
            break

        print('waiting')
        time.sleep(0.1)

"""
Retrieves historical price data for a product.
"""


from datetime import datetime, timedelta
import time
import math
import random
from textwrap import dedent
from typing import List, Generator


from cbp_client.api import API
from cbp_client.candle import Candle

ONE_MINUTE = 60
MAX_CANDLES_IN_REQUEST = 300
INTERVALS = {
    'minute': ONE_MINUTE,
    'five_minute': ONE_MINUTE * 5,
    'fifteen_minute': ONE_MINUTE * 15,
    'hourly': ONE_MINUTE * 60,
    'six_hour': ONE_MINUTE * 60 * 6,
    'daily': ONE_MINUTE * 60 * 24
}


def history(
        product_id: str,
        start: str,
        end: str,
        interval: str):
    """
    Constructs an iterable of Candles given a timeline.

    Parameters
    ----------
    product_id : str
        An identifier used by the exchange to represent a trading pair.
        Example: 'btc-usd'
    start : str
        The earliest date in the desired timeline. ISO Format YYYY-MM-DD
    end : str, Optional
        The most recent date in the desired timeline. ISO Format YYYY-MM-DD.
        Default=Today
    interval : str, Optional
        The size of each 'candle' returned.
        Options: 'one_minute', 'five_minutes', 'fifteen_minutes', 'one_hour',
        'six_hours', 'twenty_four_hours'. Default='twenty_four_hours'
    """

    timeline_start = datetime.fromisoformat(start)
    timeline_end = datetime.fromisoformat(end)

    try:
        candle_length = INTERVALS[interval]
    except KeyError as e:
        _handle_interval_error(e, interval)

    timeline = _Timeline(
        timeline_start,
        timeline_end,
        candle_length,
        product_id
    )

    return _historical_candles(timeline)


class _Timeline:
    """
    Used alongside history module for querying /candles api
    """
    def __init__(self, start, end, candle_length, product_id):
        self.product_id = product_id
        self.start = start
        self.end = end
        self.candle_length = candle_length
        self.requests_needed = self._requests_needed()

    def new(self, start, end):
        return _Timeline(start, end, self.candle_length, self.product_id)

    def _requests_needed(self):
        """
        Calculate the max number of requests needed to satisfy timeline.

        To build sufficient timelines, often more than one request is required
        to the API because only a limited number of items can be returned
        at a time.
        """
        timeline_length = (self.end - self.start).total_seconds()
        candle_count = int(timeline_length / self.candle_length)
        return math.ceil(candle_count / MAX_CANDLES_IN_REQUEST)


def _historical_candles(timeline: _Timeline, previous_end=None) -> Generator:
    """
    Chain together multiple requests to build a list of historical candles.

    The products/{product-id}/candles will only return 300 candles. If
    a request requires more than 300 candles, multiple requests are required.
    This is useful for individuals who'd like to obtain large portions of
    granual data. For example, one could use this to retrieve 2 years of hourly
    data.
    """

    for _ in range(timeline.requests_needed):

        window = _next_window(timeline, previous_end)
        data = _request_candles(window)
        time.sleep(random.uniform(0.3, 0.4))  # pause, to respect rate limits

        previous_end = window.end

        for candle in reversed(data):
            yield Candle(*candle, duration=timeline.candle_length)


def _next_window(timeline: _Timeline, previous_end: datetime) -> _Timeline:
    """"
    Return timline object with start and end date for next api request.
    """
    start = (
        previous_end + timedelta(seconds=timeline.candle_length)
        if previous_end is not None
        else timeline.start
    )

    window_length = MAX_CANDLES_IN_REQUEST * timeline.candle_length

    end = min(
        start + timedelta(seconds=window_length),
        timeline.end
    )

    if start > end:
        raise ValueError(
            f'Start must come before end. Start:{start}, End:{end}'
        )

    return timeline.new(start=start, end=end)


def _request_candles(timeline: _Timeline) -> List[Candle]:
    """
    Call /candles endpoint given proper params
    """
    endpoint = f'products/{timeline.product_id}/candles'
    params = {
        'granularity': timeline.candle_length,
        'start': timeline.start,
        'end': timeline.end,
    }

    api = API(live=True)
    return api.get(endpoint, params=params).json()


def _handle_interval_error(e, interval):
    error_message = f"""\
    "{interval}" is an invalid interval.
    Choose from: {list(INTERVALS.keys())}
    """
    raise KeyError(dedent(error_message)).with_traceback(e.__traceback__)

"""
Retrieves historical price data for a product.
"""


from datetime import datetime, timedelta
import time
import math
import random

from textwrap import dedent
from typing import Generator
from collections import namedtuple

from cbp_client.api import API
from enum import Enum


class Interval(Enum):
    ONE_MINUTE = 60
    FIVE_MINUTES = 300
    FIFTEEN_MINUTES = 900
    HOURLY = 3_600
    SIX_HOURS = 21_600
    DAILY = 86_400


class History:
    """
    Constructs an iterable of Candles given a timeline.

    Parameters
    ----------
    product_id : str
        An identifier used by the exchange to represent a trading pair.
        Example: 'btc-usd'
    start : str
        The earliest date in the desired timeline. Inclusive. ISO Format YYYY-MM-DD
    end : str, Optional
        The most recent date in the desired timeline. Inclusive. ISO Format YYYY-MM-DD.
        Default=Today
    interval : str, Optional
        The size of each 'candle' returned.
        Options: 'one_minute', 'five_minutes', 'fifteen_minutes', 'one_hour',
        'six_hours', 'twenty_four_hours'. Default='twenty_four_hours'
    quiet : bool, 'Optional
    """
    MAX_CANDLES_IN_REQUEST = 300

    Candle = namedtuple('Candle', ['start', 'open', 'high', 'low', 'close', 'volume'])

    def __init__(
        self,
        product_id: str,
        start: str,
        end: str,
        api: API,
        interval: str = Interval.DAILY.name,
        quiet: bool = True
    ):

        try:
            self.candle_length = Interval[interval].value
        except KeyError as e:
            self._handle_interval_error(e, interval)

        self._quiet = quiet
        self.api = api
        self.product_id = product_id
        self.timeline_start = datetime.fromisoformat(start)
        self.timeline_end = (
            datetime.fromisoformat(end) if isinstance(end, str)
            else datetime.now()
        )

    def __call__(self):
        return self._build_timeline()

    def _requests_needed(self):
        """
        Calculate the number of requests needed to satisfy timeline.

        To build sufficient timelines, often more than one request is required
        to the API because only a limited number of items can be returned
        at a time.
        """
        timeline_length = (
            self.timeline_end - self.timeline_start
        ).total_seconds()

        candle_count = int(timeline_length / self.candle_length)
        return math.ceil(candle_count / History.MAX_CANDLES_IN_REQUEST)

    def _build_timeline(self) -> Generator:
        """
        Chain together multiple requests to build a list of historical candles.

        The products/{product-id}/candles will only return 300 candles. If
        a request requires more than 300 candles, multiple requests are
        required. This is useful for individuals who'd like to obtain large
        portions of granual data. For example, one could use this to retrieve
        2 years of hourly data.

        Yields
        ------
        Candle : namedtuple
            Has attributes: start, open, high, low, close, volume
        """

        previous_end = None
        requests_needed = self._requests_needed()

        for _ in range(requests_needed):

            start, end = self._next_window(previous_end)
            yield from self._request_candles(start, end)

            time.sleep(random.uniform(0.3, 0.4))  # to respect rate limits
            previous_end = end

            if not self._quiet:
                print('{:=^40}'.format(' REQUEST COMPLETE '))

    def _next_window(self, previous_end: datetime) -> tuple:
        """"
        Return timline object with start and end date for next api request.
        """
        start = self.timeline_start
        if previous_end is not None:
            start = previous_end + timedelta(seconds=self.candle_length)

        shift_sec = (History.MAX_CANDLES_IN_REQUEST - 1) * self.candle_length
        window_end = start + timedelta(seconds=shift_sec)
        end = min(window_end, self.timeline_end)

        if start > end:
            raise ValueError(
                f'Start must come before end. Start:{start}, End:{end}')

        return (start, end)

    def _request_candles(self, start, end) -> Generator:
        """Call /candles endpoint given proper params"""
        candles_requested = (
            ((end - start).total_seconds() / self.candle_length) + 1
        )
        endpoint = f'products/{self.product_id}/candles'
        params = {
            'granularity': self.candle_length,
            'start': start,
            'end': end
        }

        data = self.api.get(endpoint, params=params).json()
        candles_returned = len(data)

        if candles_requested != candles_returned:
            # handle this at some point. for now, pass.
            # This might occur if requesting data during a time when
            # the api was undergoing maintanence
            pass

        return (self._to_candle(c) for c in reversed(data))

    @staticmethod
    def _handle_interval_error(e, interval):
        error_message = f"""\
        "{interval}" is an invalid interval.
        Choose from: {Interval.__members__.keys()}
        """
        raise KeyError(dedent(error_message)).with_traceback(e.__traceback__)

    @staticmethod
    def _to_candle(candle: list):
        """Converts a list to a named tuple"""
        start, low, high, open_, close, volume = candle
        start = datetime.utcfromtimestamp(start).isoformat()

        return History.Candle(
            start, str(open_), str(high), str(low), str(close), str(volume)
        )

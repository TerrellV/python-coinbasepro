from datetime import datetime, timedelta
import time
import math
import functools as ft
import itertools as it

import numpy as np

from cbp_client.api import API


class History():
    def __init__(self, base_url):
        self.api = API(base_url)
        
        self.ONE_MINUTE = 60
        self.MAX_CANDLES = 300

        self.api_granularities = {
            'minute': self.ONE_MINUTE,
            'five_minute': self.ONE_MINUTE * 5,
            'fifteen_minute': self.ONE_MINUTE * 15,
            'hourly': self.ONE_MINUTE * 60,
            'six_hour': self.ONE_MINUTE * 60 * 6,
            'daily': self.ONE_MINUTE * 60 * 24
        }

    def __call__(self, product_id, window_start_datetime, window_end_datetime, candle_interval, debug):
        
        self._set_internal_variables(product_id, window_start_datetime, window_end_datetime, candle_interval, debug)

        if self.date_range_specified:

            request_array = np.arange(1, self.required_request_count + 1)
            request_timeline = list(
                ft.reduce(self._create_request_timeline, request_array, [])
            )

            # complete all requests in the request timeline
            candles = map(self._send_request, request_timeline)
            candles = list(map(self._format_candle, it.chain(*candles)))

            return candles

        else:
            candles = self._send_request((None, None, 0))
            candles = list(map(self._format_candle, candles))
            return candles[:-1]

    def _set_internal_variables(self, product_id, window_start_datetime, window_end_datetime, candle_interval, debug):
        self.debug = debug
        self.product_id = product_id.upper()
        self.endpoint = f'products/{self.product_id}/candles'

        self.candle_length_seconds = self.api_granularities[candle_interval]
        self.candle_length_minutes = self.candle_length_seconds / self.ONE_MINUTE
        
        self.date_range_specified = window_start_datetime and window_end_datetime

        if self.date_range_specified:
            self.window_start_datetime = datetime.fromisoformat(window_start_datetime)
            self.window_end_datetime = datetime.fromisoformat(window_end_datetime) # exclusive
        else:
            return
        
        window_delta_seconds = (self.window_end_datetime - self.window_start_datetime).total_seconds()
        self.candles_in_window = int(window_delta_seconds / self.candle_length_seconds) - 1
        self.required_request_count = math.ceil(self.candles_in_window / self.MAX_CANDLES)

    def _create_request_timeline(self, accumulator, request_number):
    
        is_first_request = request_number == 1
        on_last_request = request_number == self.required_request_count
        
        one_candle_delta = timedelta(minutes=self.candle_length_minutes)
        request_delta = timedelta(minutes=self.candle_length_minutes * (self.MAX_CANDLES - 1))
        
        previous_request_end_date = accumulator[-1][1] if len(accumulator) > 0 else None
        request_start_date = self.window_start_datetime if is_first_request else previous_request_end_date + one_candle_delta
        request_end_date = self.window_end_datetime - one_candle_delta if on_last_request else request_start_date + request_delta
        wait_time = 0 if is_first_request else self.api._random_float_between_zero_one()
        accumulator.append((request_start_date, request_end_date, wait_time))
        
        return accumulator

    def _send_request(self, request_info):

        start_iso, end_iso, wait_time = request_info

        params = {
            'granularity': self.candle_length_seconds,
            'start': start_iso,
            'end': end_iso,
        }

        time.sleep(wait_time)
        candles = self.api.get(self.endpoint, params=params).json()
        
        candles.reverse()
        if self.debug:
            candle_count = len(candles)

            print(f'Candles Returned: {candle_count}\nTotal Candles Needed: {self.candles_in_window}')
            oldest_candle_datetime = datetime.utcfromtimestamp(candles[0][0]).isoformat()
            most_recent_candle_datetime = datetime.utcfromtimestamp(candles[-1][0]).isoformat()
            
            print(f'\nStart Date: {oldest_candle_datetime}\nEnd Date: {most_recent_candle_datetime}\n\n')
        
        return candles
    
    @staticmethod
    def _format_candle(candle):
        '''
        Parameters:
            candle (list): [
                'unix_timestamp',
                'low (int or float)',
                'high (int or float)',
                'open (int or float)',
                'close (int or float)',
                'volume (int or float)'
            ]
        '''

        candle_attributes = ['open_iso_datetime', 'low', 'high', 'open', 'close', 'volume']
        
        utc_datetime = datetime.utcfromtimestamp(candle[0]).isoformat()
        prices_and_volume = list(map(str, candle[1:]))
        
        candle = [utc_datetime, *prices_and_volume]
        candle = dict(zip(candle_attributes, candle))
        
        return candle

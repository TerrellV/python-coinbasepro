import pytest

from datetime import datetime
import time
import random
import types
from cbp_client.api import API
from cbp_client import history as H
from cbp_client.history import history, _Timeline
from cbp_client.candle import Candle


@pytest.fixture
def live_base_api():
    return API(live=True)


def test_history():
    candles = history('eth-usd', '2020-01-01', '2020-01-03', 'hourly')
    first_candle = next(candles)

    assert isinstance(candles, types.GeneratorType)
    assert isinstance(first_candle, Candle)

    with pytest.raises(KeyError):
        history('eth-usd', '2020-01-01', '2020-01-03', 'hours')


@pytest.mark.parametrize(
        ['start', 'end', 'candle_length', 'previous_end', 'expected_start', 'expected_end'],
        [
            ['2018-01-05', '2018-01-28', 86400, None, '2018-01-05', '2018-01-28'],
            ['2017-01-05', '2018-01-05', 86400, None, '2017-01-05', '2017-11-01'],
            ['2017-01-05', '2018-01-05', 86400, '2017-11-01', '2017-11-02', '2018-01-05'],
        ]
    )
def test_next_window(start, end, candle_length, previous_end, expected_start, expected_end):

    start = datetime.fromisoformat(start)
    end = datetime.fromisoformat(end)
    previous_end = (
        datetime.fromisoformat(previous_end)
        if previous_end is not None
        else None
    )
    t = _Timeline(start, end, 86400, 'btc-usd')

    actual = H._next_window(t, previous_end)

    assert actual.start == datetime.fromisoformat(expected_start)
    assert actual.end == datetime.fromisoformat(expected_end)


@pytest.mark.parametrize(
        ['product_id', 'granularity'],
        [
            ('btc-usd', 60 * 60 * 24),
            ('eth-usd', 60 * 60 * 24),
            ('ltc-usd', 60 * 60 * 24),
        ]
    )
def test_request_candles(product_id, granularity):
    start = datetime.fromisoformat('2017-05-01')
    end = datetime.fromisoformat('2017-05-02')
    t = _Timeline(start, end, granularity, product_id)
    data = H._request_candles(t)
    time.sleep(random.uniform(0.3, 0.4))

    assert data
    assert len(data) == 2


@pytest.mark.parametrize(
        ['start', 'end', 'candle_length', 'requests_needed'],
        [
            ('2016-01-01', '2016-11-01', 86400, 2),
            ('2016-01-01', '2016-10-01', 86400, 1),
            ('2016-01-01', '2016-12-04', 86400, 2),
            ('2016-01-01', '2017-12-05', 86400, 3),
        ])
def test_requests_needed(start, end, candle_length, requests_needed):
    start = datetime.fromisoformat(start)
    end = datetime.fromisoformat(end)
    t = _Timeline(start, end, candle_length, 'btc-usd')

    assert t.requests_needed == requests_needed


def test_historical_candles(live_base_api):
    start = datetime.fromisoformat('2020-01-01')
    end = datetime.fromisoformat('2020-01-08')
    t = _Timeline(start, end, 86400, 'btc-usd')
    g = H._historical_candles(t, None)

    assert isinstance(g, types.GeneratorType)

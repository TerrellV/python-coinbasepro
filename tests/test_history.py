
import types
from cbp_client.api import API
from cbp_client.history import History
import pytest
import pandas as pd


@pytest.fixture
def live_base_api():
    return API(sandbox_mode=False)


def test_history_default(live_base_api):
    assert History(
        product_id='eth-usd',
        start='2018-01-29',
        end='2020-02-01',
        api=live_base_api
    )


def test_history_interval_error(live_base_api):
    with pytest.raises(KeyError):
        hist = History(
            product_id='eth-usd',
            start='2020-01-01',
            end='2020-01-03',
            interval='hour',  # should be HOURLY
            api=live_base_api
        )
        hist()


def test_history_interval(live_base_api):
    hist = History(
        product_id='btc-usd',
        start='2020-01-29',
        end='2020-02-01',
        interval='FIVE_MINUTES',
        api=live_base_api
    )
    candles = hist()

    first_candle = next(candles)

    assert isinstance(candles, types.GeneratorType)
    assert isinstance(first_candle, History.Candle)


@pytest.mark.parametrize(
    'product_id, start, end, expected_candles, interval',
    [
        ['btc-usd', '2020-01-01', '2020-12-31', 366, 'DAILY'],
        ['eth-usd', '2020-07-07', '2021-07-12', 371, 'DAILY'],
        ['btc-usd', '2019-03-04', '2020-03-04', 367, 'DAILY']
    ]
)
def test_history_timeline(live_base_api, product_id, start, end, expected_candles, interval):

    hist = History(
        product_id=product_id,
        start=start,
        end=end,
        interval=interval,
        api=live_base_api
    )()

    candles = list(hist)
    expected_range = [day._date_repr for day in pd.date_range(start=start, end=end)]
    actual_range = [c.start.split('T')[0] for c in candles]

    assert len(candles) == expected_candles
    assert expected_range == actual_range

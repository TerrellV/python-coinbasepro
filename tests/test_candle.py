import pytest
from cbp_client.candle import Candle


@pytest.mark.parametrize(
        ['candle', 'expected_candle'],
        [
            (
                [1420674445, 2001, 2200, 2050, 2100.0, 37000, 86400],
                ['2015-01-07T23:47:25', '2050', '2200', '2001', '2100.0', '37000']
            ),
            (
                [1420834445, 2001.32, 2200, 2050, 2100.0, 37000, 86400],
                ['2015-01-09T20:14:05', '2050', '2200', '2001.32', '2100.0', '37000']
            )

        ]
    )
def test_candle(candle, expected_candle):

    actual_candle = Candle(*candle)
    actual_attributes = [a for a in actual_candle.__dict__.keys() if '_' not in a]
    expected_attributes = ['start', 'open', 'high', 'low', 'close', 'volume']
    assert isinstance(actual_candle, Candle)
    assert len(actual_candle.to_list()) == 6
    assert actual_candle.to_list() == expected_candle
    assert actual_attributes == expected_attributes



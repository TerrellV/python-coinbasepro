"""
Represents a breif period of trading activity for an asset.
"""


from textwrap import dedent
from datetime import datetime


class Candle:
    def __init__(self, start, low, high, open_, close, volume, duration):
        self._start = start
        self.start = datetime.utcfromtimestamp(start).isoformat()
        self.open = str(open_)
        self.high = str(high)
        self.low = str(low)
        self.close = str(close)
        self.volume = str(volume)
        self._duration = duration

        string = f"""\
            Candle(
                start={self.start},
                open={self.open},
                high={self.high},
                low={self.low},
                close={self.close},
                volume={self.volume},
            )
        """

        self._str = string

    def __len__(self):
        public_attrs = [a for a in self.__dict__.values() if '_' not in a]
        return len(public_attrs)

    def to_list(self):
        """
        Return public attributes as a list, exluding attr that start with _
        """
        return [v for k,v in self.__dict__.items() if '_' not in k]

    def __repr__(self):
        return dedent(self._str)

    def __str__(self):
        return dedent(self._str)
from math import ceil, floor
from pint import UnitRegistry

from speed_miner.misc.logging import LOG


class Rate(object):

    def __init__(self, rate_str):
        self._quantity = Benchmarker.ureg(rate_str)

        assert self._quantity.dimensionality == "[hash] / [time]" or \
            self._quantity.dimensionality == "[solution] / [time]"

    def get_mbtc_per_day(self, profitability):
        profitability = Benchmarker.ureg(profitability).to_base_units()
        assert profitability.dimensionality == "[currency] / [hash]" or \
            profitability.dimensionality == "[currency] / [solution]", \
            "Bad dimensionality: %s" % profitability.dimensionality
        return (self._quantity * profitability).to("mbtc / day").magnitude

    def to_base_units(self, *args, **kwargs):
        return Rate(str(self._quantity.to_base_units(*args, **kwargs)))

    def __add__(self, other):
        return Rate(str(self._quantity.__add__(other._quantity)))

    def __eq__(self, other):
        if other is None:
            return False
        return self._quantity.__eq__(other._quantity)

    def __floordiv__(self, other):
        if isinstance(other, Rate):
            rate = self._quantity.__floordiv__(other._quantity)
        else:
            rate = self._quantity.__floordiv__(other)

        return Rate(str(rate))

    def __ne__(self, other):
        if other is None:
            return True
        return self._quantity.__ne__(other._quantity)

    def __lt__(self, other):
        return self._quantity.__lt__(other._quantity)

    def __le__(self, other):
        return self._quantity.__le__(other._quantity)

    def __gt__(self, other):
        return self._quantity.__gt__(other._quantity)

    def __ge__(self, other):
        return self._quantity.__ge__(other._quantity)

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __str__(self):
        return str(self._quantity)

    def __truediv__(self, other):
        if isinstance(other, Rate):
            rate = self._quantity.__truediv__(other._quantity)
        else:
            rate = self._quantity.__truediv__(other)

        return Rate(str(rate))


class Benchmarker(object):

    @staticmethod
    def init_unit_reg():
        ureg = UnitRegistry()

        ureg.define("hash = [hash] = h")
        ureg.define("solution = [solution] = sol")
        ureg.define("bitcoin = [currency] = btc")

        ureg.default_format = '~'

        Benchmarker.ureg = ureg

    def __init__(self, benching_thresh=.1, benching_dir_window=10):

        self._rates = []
        self._direction = []

        self._benching_thresh = benching_thresh
        self._benching_dir_window = benching_dir_window

    def add_rate(self, rate):
        LOG.debug("Rate added: %s...", rate)

        if len(self._rates) > 0:
            if rate > self._rates[-1]:
                self._direction.append(1)
            elif rate == self._rates[-1]:
                self._direction.append(0.5)
            else:
                self._direction.append(0)

        self._rates.append(rate)

    def get_benchmark(self):
        if len(self._direction) < self._benching_dir_window:
            return None

        upper_bound = ceil(self._benching_dir_window * (0.5 + self._benching_thresh))
        lower_bound = floor(self._benching_dir_window * (0.5 - self._benching_thresh))
        num_inc = sum(self._direction[-self._benching_dir_window:])

        if num_inc >= lower_bound and num_inc <= upper_bound:
            rates = self._rates[-(self._benching_dir_window + 1):]
            return (sum(rates) / len(rates)).to_base_units()
        else:
            return None


Benchmarker.init_unit_reg()

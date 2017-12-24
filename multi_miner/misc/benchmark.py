from enum import auto, Enum, unique
from math import ceil, floor

from multi_miner.misc.logger import pr


@unique
class BenchmarkUnit(Enum):
    HASH_SEC = 'h/s'
    KILO_HASH_SEC = 'kh/s'
    MEGA_HASH_SEC = 'mh/s'
    GIGA_HASH_SEC = 'gh/s'
    TERA_HASH_SEC = 'th/s'
    SOL_SEC = 'sol/s'

    @staticmethod
    def unit_from_str(unit_str):
        unit_str = unit_str.strip().lower()

        if unit_str == "h/s":
            return BenchmarkUnit.HASH_SEC
        if unit_str == "kh/s":
            return BenchmarkUnit.KILO_HASH_SEC
        elif unit_str == "mh/s":
            return BenchmarkUnit.MEGA_HASH_SEC
        elif unit_str == "gh/s":
            return BenchmarkUnit.GIGA_HASH_SEC
        elif unit_str == "th/s":
            return BenchmarkUnit.TERA_HASH_SEC
        elif unit_str == "sol/s":
            return BenchmarkUnit.SOL_SEC
        else:
            raise Exception("Unsupported unit: %s" % unit_str)

    def __str__(self):
        return self.value


class Benchmark(object):
    def __init__(self, rate, unit):
        assert unit in BenchmarkUnit, "Unit is not a proper benchmarking unit"

        if unit == BenchmarkUnit.HASH_SEC:
            rate = rate / 1000000
            unit = BenchmarkUnit.MEGA_HASH_SEC
        elif unit == BenchmarkUnit.KILO_HASH_SEC:
            rate = rate / 1000
            unit = BenchmarkUnit.MEGA_HASH_SEC
        elif unit == BenchmarkUnit.GIGA_HASH_SEC:
            rate = rate * 1000
            unit = BenchmarkUnit.MEGA_HASH_SEC
        elif unit == BenchmarkUnit.TERA_HASH_SEC:
            rate = rate * 1000000
            unit = BenchmarkUnit.MEGA_HASH_SEC

        self.rate = rate
        self.unit = unit

    def get_rate(self):
        return self.rate

    def get_unit(self):
        return self.unit

    def get_24_hour_profitability(self, profitability, unit):
        # Profitability is usually mBTC / (rate)
        # Convert to the standard rate of sol or mh.
        if unit == "kh":
            profitability = profitability * 1000
        elif unit == "gh" or unit == "ks":
            profitability = profitability / 1000
        elif unit == "th" or unit == "ms":
            profitability = profitability / 1000000
        elif unit == "ph":
            profitability = profitability / 1000000000
        elif unit != "s" and unit != "mh":
            raise Exception("Unsupported unit: %s" % unit)

        return profitability * self.rate

    def __str__(self):
        return "%0.2f %s" % (self.get_rate(), self.get_unit())


class Benchmarker(object):
    BENCHING_DIR_WINDOW = 10
    BENCHING_THRESH = .1

    def __init__(self):
        self.rates = []
        self.direction = []

    def add_rate(self, rate, unit):
        b = Benchmark(rate, unit)
        pr("Rate added: %s...\n" % b, prefix="Benchmarker")

        if len(self.rates) > 0:
            if b.get_rate() > self.rates[-1].get_rate():
                self.direction.append(1)
            elif b.get_rate() == self.rates[-1].get_rate():
                self.direction.append(0.5)
            else:
                self.direction.append(0)

        self.rates.append(b)

    def get_benchmark(self):
        if len(self.direction) < Benchmarker.BENCHING_DIR_WINDOW:
            return None

        upper_bound = ceil(Benchmarker.BENCHING_DIR_WINDOW * (.5 + Benchmarker.BENCHING_THRESH))
        lower_bound = floor(Benchmarker.BENCHING_DIR_WINDOW * (.5 - Benchmarker.BENCHING_THRESH))
        num_inc = sum(self.direction[-Benchmarker.BENCHING_DIR_WINDOW:])
        #print(upper_bound, lower_bound, num_inc)

        if num_inc >= lower_bound and num_inc <= upper_bound:
            rates = self.rates[-(Benchmarker.BENCHING_DIR_WINDOW + 1):]
            avg = sum((r.get_rate() for r in rates)) / len(rates)
            unit = rates[0].get_unit()
            b = Benchmark(avg, unit)
            return b
        else:
            return None

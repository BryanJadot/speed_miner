from enum import Enum, unique


@unique
class BenchmarkUnit(Enum):
    KILO_HASH_SEC = 0
    MEGA_HASH_SEC = 1
    GIGA_HASH_SEC = 2
    TERA_HASH_SEC = 3
    SOL_SEC = 4

    @staticmethod
    def unit_from_str(unit_str):
        unit_str = unit_str.trim().lower()

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


class Benchmark(object):
    def __init__(self, rate, unit):
        assert unit in BenchmarkUnit, "Unit is not a proper benchmarking unit"

        if unit == KILO_HASH_SEC:
            rate = rate / 1000
            unit = BenchmarkUnit.MEGA_HASH_SEC
        elif unit == GIGA_HASH_SEC:
            rate = rate * 1000
            unit = BenchmarkUnit.MEGA_HASH_SEC
        elif unit == TERA_HASH_SEC:
            rate = rate * 1000000
            unit = BenchmarkUnit.MEGA_HASH_SEC

        self.rate = rate
        self.unit = unit

    def get_rate():
        return self.rate

    def get_unit():
        return self.unit

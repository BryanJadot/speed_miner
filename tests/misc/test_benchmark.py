from speed_miner.misc.benchmark import Benchmarker, Rate

from tests.util.test_case import MinerTestCase


class TestRate(MinerTestCase):

    def setUp(self):
        self.hr1 = Rate("20 Mh/s")
        self.hr2 = Rate("20 Mh/s")
        self.hr3 = Rate("20 kh/s")

    def test_init(self):
        with self.assertRaises(AssertionError):
            Rate("1 Mh/s/s")

    def test_rate_profitability(self):
        self.assertEqual(self.hr1.get_mbtc_per_day("0.05 mbtc*s/day/Mh"), 1.0)

    def test_rate_to_base_units(self):
        self.assertEqual(str(self.hr1.to_base_units()), "20000000.0 h / s")

    def test_rate_cmp(self):
        self.assertTrue(self.hr1 > self.hr3)
        self.assertFalse(self.hr3 > self.hr1)

        self.assertTrue(self.hr3 < self.hr2)
        self.assertFalse(self.hr2 < self.hr3)

        self.assertTrue(self.hr3 <= self.hr2)
        self.assertTrue(self.hr1 <= self.hr2)
        self.assertFalse(self.hr2 <= self.hr3)

        self.assertTrue(self.hr2 >= self.hr3)
        self.assertTrue(self.hr2 >= self.hr1)
        self.assertFalse(self.hr3 >= self.hr2)

        self.assertTrue(self.hr1 == self.hr2)
        self.assertFalse(self.hr1 == self.hr3)
        self.assertFalse(self.hr1 == None)  # NOQA

        self.assertTrue(self.hr1 != self.hr3)
        self.assertFalse(self.hr1 != self.hr2)
        self.assertTrue(self.hr1 != None)  # NOQA

    def test_rate_add(self):
        self.assertEqual(self.hr1 + self.hr2, Rate("40 Mh/s"))

    def test_rate_str(self):
        self.assertEqual(str(self.hr1), "20.0 Mh / s")

    def test_rate_solution_simple(self):
        r = Rate("20 ksol/s")
        self.assertEqual(str(r), "20.0 ksol / s")
        self.assertEqual(str(r.to_base_units()), "20000.0 sol / s")


class TestBenchmarker(MinerTestCase):

    def setUp(self):
        self.b = Benchmarker(benching_thresh=.1, benching_dir_window=5)

    def test_add_rate(self):
        self.b.add_rate(Rate("20 Mh / s"))
        self.b.add_rate(Rate("20 Mh / s"))
        self.b.add_rate(Rate("200 kh / s"))
        self.b.add_rate(Rate("19 Mh / s"))

    def test_benchmark_under_window(self):
        self.assertIsNone(self.b.get_benchmark())

        self.b.add_rate(Rate("20 Mh / s"))
        self.assertIsNone(self.b.get_benchmark())

        self.b.add_rate(Rate("20 Mh / s"))
        self.assertIsNone(self.b.get_benchmark())

    def test_benchmark_inc(self):
        self.b.add_rate(Rate("20 Mh / s"))
        self.b.add_rate(Rate("20 Mh / s"))
        self.b.add_rate(Rate("21 Mh / s"))
        self.b.add_rate(Rate("22 Mh / s"))
        self.b.add_rate(Rate("23 Mh / s"))
        self.b.add_rate(Rate("24 Mh / s"))
        self.assertIsNone(self.b.get_benchmark())

    def test_benchmark_dec(self):
        self.b.add_rate(Rate("20 Mh / s"))
        self.b.add_rate(Rate("20 Mh / s"))
        self.b.add_rate(Rate("19 Mh / s"))
        self.b.add_rate(Rate("18 Mh / s"))
        self.b.add_rate(Rate("17 Mh / s"))
        self.b.add_rate(Rate("16 Mh / s"))
        self.assertIsNone(self.b.get_benchmark())

    def test_benchmark_bench_simple(self):
        self.b.add_rate(Rate("20 Mh / s"))
        self.b.add_rate(Rate("20 Mh / s"))
        self.b.add_rate(Rate("20 Mh / s"))
        self.b.add_rate(Rate("20 Mh / s"))
        self.b.add_rate(Rate("20 Mh / s"))
        self.b.add_rate(Rate("20 Mh / s"))
        self.assertEqual(self.b.get_benchmark(), Rate("20 Mh / s"))

    def test_benchmark_bench_more_complex(self):
        self.b.add_rate(Rate("20 Mh / s"))
        self.b.add_rate(Rate("21 Mh / s"))
        self.b.add_rate(Rate("22 Mh / s"))
        self.b.add_rate(Rate("23 Mh / s"))
        self.b.add_rate(Rate("24 Mh / s"))
        self.b.add_rate(Rate("25 Mh / s"))
        self.b.add_rate(Rate("26 Mh / s"))
        self.b.add_rate(Rate("24 Mh / s"))
        self.b.add_rate(Rate("25 Mh / s"))
        self.b.add_rate(Rate("26 Mh / s"))

        self.assertEqual(self.b.get_benchmark(), None)

        self.b.add_rate(Rate("26 Mh / s"))
        self.b.add_rate(Rate("25 Mh / s"))
        self.b.add_rate(Rate("24 Mh / s"))

        self.assertEqual(self.b.get_benchmark(), Rate("25 Mh / s"))

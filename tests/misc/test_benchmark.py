from speed_miner.misc.benchmark import Benchmarker, Rate

from tests.util.test_case import MinerTestCase


class TestRate(MinerTestCase):

    def setUp(self):
        self.hr1 = Rate("20 MH/s")
        self.hr2 = Rate("20 MH/s")
        self.hr3 = Rate("20 kH/s")

    def test_init(self):
        with self.assertRaises(AssertionError):
            Rate("1 MH/s/s")

        self.assertEqual(str(Rate("9014.51MH/s")), "9014.51 MH / s")
        self.assertEqual(str(Rate("9014.51 MH/s")), "9014.51 MH / s")
        self.assertEqual(str(Rate("9014.51 MH / s")), "9014.51 MH / s")

        self.assertEqual(str(Rate("9014.51kSol/s")), "9014.51 kSol / s")
        self.assertEqual(str(Rate("9014.51 kSol/s")), "9014.51 kSol / s")
        self.assertEqual(str(Rate("9014.51 kSol / s")), "9014.51 kSol / s")

    def test_rate_profitability(self):
        self.assertEqual(self.hr1.get_mbtc_per_day("0.05 mBTC*s/day/MH"), 1.0)

    def test_rate_to_base_units(self):
        self.assertEqual(str(self.hr1.to_base_units()), "20000000.0 H / s")

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

        self.assertFalse(self.hr1 == self.hr3)
        self.assertFalse(self.hr1 == None)  # NOQA

        self.assertTrue(self.hr1 != self.hr3)
        self.assertFalse(self.hr1 != self.hr2)
        self.assertTrue(self.hr1 != None)  # NOQA

    def test_rate_add(self):
        self.assertEqual(self.hr1 + self.hr2, Rate("40 MH/s"))

    def test_rate_str(self):
        self.assertEqual(str(self.hr1), "20.0 MH / s")

    def test_rate_solution_simple(self):
        r = Rate("20 kSol/s")
        self.assertEqual(str(r), "20.0 kSol / s")
        self.assertEqual(str(r.to_base_units()), "20000.0 Sol / s")


class TestBenchmarker(MinerTestCase):

    def setUp(self):
        self.b = Benchmarker(benching_thresh=.1, benching_dir_window=5)

    def test_add_rate(self):
        self.b.add_rate(Rate("20 MH / s"))
        self.b.add_rate(Rate("20 MH / s"))
        self.b.add_rate(Rate("200 kH / s"))
        self.b.add_rate(Rate("19 MH / s"))

    def test_benchmark_under_window(self):
        self.assertIsNone(self.b.get_benchmark())

        self.b.add_rate(Rate("20 MH / s"))
        self.assertIsNone(self.b.get_benchmark())

        self.b.add_rate(Rate("20 MH / s"))
        self.assertIsNone(self.b.get_benchmark())

    def test_benchmark_inc(self):
        self.b.add_rate(Rate("20 MH / s"))
        self.b.add_rate(Rate("20 MH / s"))
        self.b.add_rate(Rate("21 MH / s"))
        self.b.add_rate(Rate("22 MH / s"))
        self.b.add_rate(Rate("23 MH / s"))
        self.b.add_rate(Rate("24 MH / s"))
        self.assertIsNone(self.b.get_benchmark())

    def test_benchmark_dec(self):
        self.b.add_rate(Rate("20 MH / s"))
        self.b.add_rate(Rate("20 MH / s"))
        self.b.add_rate(Rate("19 MH / s"))
        self.b.add_rate(Rate("18 MH / s"))
        self.b.add_rate(Rate("17 MH / s"))
        self.b.add_rate(Rate("16 MH / s"))
        self.assertIsNone(self.b.get_benchmark())

    def test_benchmark_bench_simple(self):
        self.b.add_rate(Rate("20 MH / s"))
        self.b.add_rate(Rate("20 MH / s"))
        self.b.add_rate(Rate("20 MH / s"))
        self.b.add_rate(Rate("20 MH / s"))
        self.b.add_rate(Rate("20 MH / s"))
        self.b.add_rate(Rate("20 MH / s"))
        self.assertEqual(self.b.get_benchmark(), Rate("20 MH / s"))

    def test_benchmark_bench_more_complex(self):
        self.b.add_rate(Rate("20 MH / s"))
        self.b.add_rate(Rate("21 MH / s"))
        self.b.add_rate(Rate("22 MH / s"))
        self.b.add_rate(Rate("23 MH / s"))
        self.b.add_rate(Rate("24 MH / s"))
        self.b.add_rate(Rate("25 MH / s"))
        self.b.add_rate(Rate("26 MH / s"))
        self.b.add_rate(Rate("24 MH / s"))
        self.b.add_rate(Rate("25 MH / s"))
        self.b.add_rate(Rate("26 MH / s"))

        self.assertEqual(self.b.get_benchmark(), None)

        self.b.add_rate(Rate("26 MH / s"))
        self.b.add_rate(Rate("25 MH / s"))
        self.b.add_rate(Rate("24 MH / s"))

        self.assertEqual(self.b.get_benchmark(), Rate("25 MH / s"))

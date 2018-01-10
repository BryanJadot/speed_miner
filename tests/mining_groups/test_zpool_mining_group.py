from unittest.mock import patch

from speed_miner.mining_groups.zpool_mining_group import ZPoolMiningGroupLoader

from tests.util.test_case import MinerTestCase


class TestMinerConfigLoader(MinerTestCase):

    def setUp(self):
        self.c = ZPoolMiningGroupLoader()

    def test_good_dict_parse(self):
        d = {
            "payout_currency": "btc",
            "algo_blacklist": "skein, equihash",
            "algo_data_source": "currency",
            "calc_all_algo_data_sources": "true",
        }
        config = self.c.process_config_from_dict(d)
        self.assertEqual(config["payout_currency"], "BTC")
        self.assertEqual(config["algo_blacklist"], {"skein", "equihash"})
        self.assertEqual(config["algo_data_source"], "currency")
        self.assertEqual(config["calc_all_algo_data_sources"], True)

        d = {
            "payout_currency": "btc",
        }
        config = self.c.process_config_from_dict(d)
        self.assertEqual(config["payout_currency"], "BTC")
        self.assertEqual(config["algo_blacklist"], set())
        self.assertEqual(config["algo_data_source"], "algo")
        self.assertEqual(config["calc_all_algo_data_sources"], False)

    def _check_desc(self, _exit, _print):
        _exit.assert_called_with(1)
        desc = _print.call_args[0][0]
        self.assertIn("Looks like you're trying", desc)
        self.assertIn("A list of algos to not mine", desc)
        self.assertIn("Put the desired", desc)
        self.assertIn("profitability from all", desc)
        self.assertIn("default: \"algo\"", desc)
        self.assertIn("default: \"\"", desc)
        self.assertIn("default: \"false\"", desc)

    @patch("speed_miner.misc.config_loader.print")
    @patch("speed_miner.misc.config_loader.exit")
    def test_bad_param(self, _exit, _print):
        d = {
            "payout_currency": "btc",
            "algo_blacklist": "skein, equihash",
            "algo_data_source": "currencfdsay",
        }
        self.c.process_config_from_dict(d)
        self._check_desc(_exit, _print)

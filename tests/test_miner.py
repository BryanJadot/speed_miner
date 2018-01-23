from unittest.mock import patch

from speed_miner.miner import MinerConfigLoader

from tests.util.test_case import MinerTestCase


class TestMinerConfigLoader(MinerTestCase):

    def setUp(self):
        self.c = MinerConfigLoader()

    def test_good_dict_parse(self):
        d = {
            "group": "zpool",
            "wallet": "123",
            "log_level": "DEBUG",
        }
        config = self.c.process_config_from_dict(d)
        self.assertEqual(config["group"].__name__, "ZPoolMiningGroup")
        self.assertEqual(config["wallet"], "123")
        self.assertEqual(config["log_level"], 10)

        d = {
            "group": "zpool",
            "wallet": "123",
        }
        config = self.c.process_config_from_dict(d)
        self.assertEqual(config["group"].__name__, "ZPoolMiningGroup")
        self.assertEqual(config["wallet"], "123")
        self.assertEqual(config["log_level"], 20)

    def _check_desc(self, _print):
        desc = _print.call_args[0][0]
        self.assertIn("Let's mine some coin", desc)
        self.assertIn("CRITICAL", desc)
        self.assertIn("default: \"INFO\"", desc)

    @patch("speed_miner.misc.config_loader.print")
    def test_bad_param(self, _print):
        d = {}
        with self.assertRaises(SystemExit):
            self.c.process_config_from_dict(d)
        self._check_desc(_print)

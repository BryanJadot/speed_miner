from json import dumps
from unittest.mock import mock_open, patch

from speed_miner.misc.config_loader import InvalidMiningConfig, MiningConfigLoader

from tests.util.test_case import MinerTestCase


class DummyConfigLoader(MiningConfigLoader):

    def describe(self):
        return "This is a dummy desc"

    def describe_param(self):
        return "This is a description for param"

    def parse_param(self, param):
        if param == "good":
            return 0
        else:
            raise InvalidMiningConfig("bad")

    def describe_param1(self):
        return ("yay", "This is a default param description")

    def default_parse_param1(self, param):
        if param is None:
            return 1
        elif param == "yay":
            return 0
        else:
            raise InvalidMiningConfig("bad")


class TestDummyConfigLoader(MinerTestCase):

    def setUp(self):
        self.c = DummyConfigLoader()

    def test_good_dict_parse(self):
        d = {
            "param": "good",
            "param1": "yay",
        }
        config = self.c.process_config_from_dict(d)
        self.assertEqual(config["param"], 0)
        self.assertEqual(config["param1"], 0)

        d = {
            "param": "good",
        }
        config = self.c.process_config_from_dict(d)
        self.assertEqual(config["param"], 0)
        self.assertEqual(config["param1"], 1)

        d = {
            "param": "good",
            "fdsasdf": "fdsfsd",
        }
        config = self.c.process_config_from_dict(d)
        self.assertEqual(config["param"], 0)
        self.assertEqual(config["param1"], 1)
        self.assertNotIn("fdsasdf", config)

    def test_good_file_parse(self):
        d = {
            "param": "good",
            "param1": "yay",
        }
        with patch("speed_miner.misc.config_loader.open", mock_open(read_data=dumps(d))):
            config = self.c.process_config_from_file("")
            self.assertEqual(config["param"], 0)
            self.assertEqual(config["param1"], 0)

        d = {
            "param": "good",
        }
        with patch("speed_miner.misc.config_loader.open", mock_open(read_data=dumps(d))):
            config = self.c.process_config_from_file("")
            self.assertEqual(config["param"], 0)
            self.assertEqual(config["param1"], 1)

    def _check_desc(self, _exit, _print, err_str):
        _exit.assert_called_with(1)
        desc = _print.call_args[0][0]
        self.assertIn(self.c.describe(), desc)
        self.assertIn(self.c.describe_param(), desc)
        self.assertIn("default: \"%s\"" % self.c.describe_param1()[0], desc)
        self.assertIn(self.c.describe_param1()[1], desc)
        self.assertIn(err_str, desc)

    @patch("speed_miner.misc.config_loader.print")
    @patch("speed_miner.misc.config_loader.exit")
    def test_bad_param(self, _exit, _print):
        d = {
            "param": "bad",
            "param1": "yay",
        }
        self.c.process_config_from_dict(d)
        self._check_desc(_exit, _print, "\"bad\"")

        d = {
            "param": "good",
        }
        self.c.process_config_from_dict(d)
        self._check_desc(_exit, _print, "\"bad\"")

    @patch("speed_miner.misc.config_loader.print")
    @patch("speed_miner.misc.config_loader.exit")
    def test_bad_file_parse(self, _exit, _print):
        with patch("speed_miner.misc.config_loader.open", mock_open(read_data="fdsa.fds//")):
            self.c.process_config_from_file("")
            self._check_desc(_exit, _print, "Config file is not JSON formatted")

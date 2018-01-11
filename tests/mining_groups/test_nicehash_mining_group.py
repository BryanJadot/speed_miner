from json import loads
from unittest.mock import MagicMock, patch

from speed_miner.mining_groups.nicehash_mining_group import (
    NicehashMiningGroup,
    NicehashMiningGroupLoader,
)
from speed_miner.miner import MinerConfigLoader
from speed_miner.misc.config_loader import MiningConfigManager

from tests.util.test_case import MinerTestCase


class TestNicehashMinerConfigLoader(MinerTestCase):

    def setUp(self):
        self.c = NicehashMiningGroupLoader()

    def test_good_dict_parse(self):
        d = {
            "algo_blacklist": "skein, equihash",
        }
        config = self.c.process_config_from_dict(d)
        self.assertEqual(config["algo_blacklist"], {"skein", "equihash"})

        d = {
        }
        config = self.c.process_config_from_dict(d)
        self.assertEqual(config["algo_blacklist"], set())


class TestNicehashMiningGroup(MinerTestCase):

    def test_get_group_config_loader(self):
        self.assertTrue(isinstance(
            NicehashMiningGroup.get_group_config_loader(), NicehashMiningGroupLoader))

    def test_init_from_config(self):
        d = {
            "wallet": "fdsa",
            "group": "nicehash",
        }
        config_man = MiningConfigManager()

        main_config_loader = MinerConfigLoader()
        config_man.load_from_dict(main_config_loader, d)

        group_config_loader = NicehashMiningGroupLoader()
        config_man.load_from_dict(group_config_loader, d)

        config = config_man.get_config()

        self.assertTrue(isinstance(
            NicehashMiningGroup.init_from_config(config), NicehashMiningGroup))

    def _get_currency_api_resp(self):
        return loads('{"result":{"simplemultialgo":[{"paying":"0.00235977","port":3333,"name":"scrypt","algo":0},{"paying":"0.00000016","port":3334,"name":"sha256","algo":1},{"paying":"0","port":3335,"name":"scryptnf","algo":2},{"paying":"0.0000382","port":3336,"name":"x11","algo":3},{"paying":"0.00084368","port":3337,"name":"x13","algo":4},{"paying":"0.00034611","port":3338,"name":"keccak","algo":5},{"paying":"0.00020432","port":3339,"name":"x15","algo":6},{"paying":"0.00961986","port":3340,"name":"nist5","algo":7},{"paying":"0.39292752","port":3341,"name":"neoscrypt","algo":8},{"paying":"0","port":3342,"name":"lyra2re","algo":9},{"paying":"0","port":3343,"name":"whirlpoolx","algo":10},{"paying":"0.00044468","port":3344,"name":"qubit","algo":11},{"paying":"0.00060125","port":3345,"name":"quark","algo":12},{"paying":"0","port":3346,"name":"axiom","algo":13},{"paying":"0.00751485","port":3347,"name":"lyra2rev2","algo":14},{"paying":"0","port":3348,"name":"scryptjanenf16","algo":15},{"paying":"0","port":3349,"name":"blake256r8","algo":16},{"paying":"0","port":3350,"name":"blake256r14","algo":17},{"paying":"0","port":3351,"name":"blake256r8vnl","algo":18},{"paying":"177.03964972","port":3352,"name":"hodl","algo":19},{"paying":"0.01134898","port":3353,"name":"daggerhashimoto","algo":20},{"paying":"0.00005438","port":3354,"name":"decred","algo":21},{"paying":"388.69233476","port":3355,"name":"cryptonight","algo":22},{"paying":"0.00064669","port":3356,"name":"lbry","algo":23},{"paying":"783.50452989","port":3357,"name":"equihash","algo":24},{"paying":"0.00015507","port":3358,"name":"pascal","algo":25},{"paying":"0.02264525","port":3359,"name":"x11gost","algo":26},{"paying":"0.00006761","port":3360,"name":"sia","algo":27},{"paying":"0.00006948","port":3361,"name":"blake2s","algo":28},{"paying":"0.01034467","port":3362,"name":"skunk","algo":29}]},"method":"simplemultialgo.info"}')  # NOQA

    def _get_miner_mock(self, algo, *args, **kwargs):
        miner = MagicMock()
        rate = MagicMock()
        miner._algo = algo
        if algo == "equihash":
            rate.get_mbtc_per_day = lambda x: 10000000.0
        elif algo == "lyra2v2":
            rate.get_mbtc_per_day = lambda x: 5.0
        else:
            rate.get_mbtc_per_day = lambda x: 0.0

        miner.benchmark = lambda: rate

        return miner

    @patch("speed_miner.mining_groups.zpool_mining_group.Fetcher.fetch_json_api")
    @patch("speed_miner.mining_groups.multipool_mining_group.get_miner_for_algo")
    def test_get_most_profitable_miner_algo(self, get_miner_for_algo, fetch_json_api):
        get_miner_for_algo.side_effect = self._get_miner_mock
        fetch_json_api.return_value = self._get_currency_api_resp()
        z = NicehashMiningGroup("BTC", "fdsafdsafdsa")
        miner = z.get_most_profitable_miner()
        fetch_json_api.assert_called_with(
            "https://api.nicehash.com/api?method=simplemultialgo.info")
        self.assertEqual(miner._algo, "equihash")

    @patch("speed_miner.mining_groups.zpool_mining_group.Fetcher.fetch_json_api")
    @patch("speed_miner.mining_groups.multipool_mining_group.get_miner_for_algo")
    def test_get_most_profitable_miner_algo_blacklist(self, get_miner_for_algo, fetch_json_api):
        get_miner_for_algo.side_effect = self._get_miner_mock
        fetch_json_api.return_value = self._get_currency_api_resp()
        z = NicehashMiningGroup("fdsafdsafdsa", algo_blacklist={"equihash"})
        miner = z.get_most_profitable_miner()
        fetch_json_api.assert_called_with(
            "https://api.nicehash.com/api?method=simplemultialgo.info")
        self.assertEqual(miner._algo, "lyra2v2")

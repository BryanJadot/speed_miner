from speed_miner.mining_groups.multipool_mining_group import (
    AlgoInfo,
    MultipoolMiningGroup,
    MultipoolMiningGroupLoader,
)
from speed_miner.misc.fetcher import Fetcher
from speed_miner.misc.logging import LOG


class NicehashMiningGroupLoader(MultipoolMiningGroupLoader):
    def describe(self):
        return "Looks like you're trying to mine Nicehash!"


class NicehashMiningGroup(MultipoolMiningGroup):
    NICEHASH_URL_SUFFIX = ".usa.nicehash.com"

    @staticmethod
    def get_group_config_loader():
        return NicehashMiningGroupLoader()

    @staticmethod
    def init_from_config(config):
        return NicehashMiningGroup(config["wallet"], algo_blacklist=config["algo_blacklist"])

    def _generate_password(self, algo):
        return "x"

    def _get_nicehash_profitability_unit(self, algo):
        if algo == "equihash":
            return "Msol"
        return "MH"

    def _get_prof_str(self, estimate, algo):
        return "%s mbtc/%s*s/day" % (estimate, self._get_nicehash_profitability_unit(algo))

    def _get_url(self, algo):
        return "stratum+tcp://%s%s" % (algo, NicehashMiningGroup.NICEHASH_URL_SUFFIX)

    def _num_to_algo(self, algo_num):
        return {
            0: "scrypt",
            1: "sha256",
            2: "scryptnf",
            3: "x11",
            4: "x13",
            5: "keccak",
            6: "x15",
            7: "nist5",
            8: "neoscrypt",
            9: "lyra2re",
            10: "whirlpoolx",
            11: "qubit",
            12: "quark",
            13: "axiom",
            14: "lyra2rev2",
            15: "scryptjanenf16",
            16: "blake256r8",
            17: "blake256r14",
            18: "blake256r8vnl",
            19: "hodl",
            20: "daggerhashimoto",
            21: "decred",
            22: "cryptonight",
            23: "lbry",
            24: "equihash",
            25: "pascal",
            26: "x11gost",
            27: "sia",
            28: "blake2s",
            29: "skunk",
        }[algo_num]

    def _to_algo_info(self, currencies):
        algo_info_dict = {}

        for c in currencies:
            algo = self._num_to_algo(c["algo"])
            url_algo = algo
            if algo == "lyra2rev2":
                algo = "lyra2v2"
            if algo not in algo_info_dict:
                algo_info_dict[algo] = AlgoInfo(
                    algo=algo,
                    prof_str=self._get_prof_str(c["paying"], algo),
                    port=c["port"],
                    url=self._get_url(url_algo),
                )

        return list(algo_info_dict.values())

    def _get_algo_info(self):
        LOG.debug("Fetching currency info...")
        d = list(list(Fetcher.fetch_json_api(
            "https://api.nicehash.com/api?method=simplemultialgo.info").values())[0].values())[0]
        return self._to_algo_info(d)

    def __str__(self):
        return "Nicehash Mining Group"

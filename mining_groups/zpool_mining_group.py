from subprocess import PIPE, Popen

from multi_miner.miners.ccminer import CCMiner
from multi_miner.mining_groups.abstract_mining_group import AbstractMiningGroup
from multi_miner.misc.fetcher import Fetcher
from multi_miner.misc.logger import pr
from multi_miner.misc.wallets import Wallets


class ZPoolMiningGroup(AbstractMiningGroup):
    ZPOOL_URL_SUFFIX = ".mine.zpool.ca"
    BLACKLISTED_ALGOS = set(["scrypt"])

    def __init__(self, payout_currency):
        self._payout_currency = payout_currency

    def _get_zpool_profitability_unit(self, algo):
        if algo == "sha256":
            return "ph"
        elif algo == "scrypt":
            return "gh"
        elif algo == "equihash":
            return "ks"
        elif algo == "neoscrypt":
            return "mh"
        elif algo == "quark":
            return "gh"
        elif algo == "blake2s":
            return "gh"
        elif algo == "blakecoin":
            return "gh"
        elif algo == "xevan":
            return "mh"
        elif algo == "decred":
            return "gh"
        elif algo == "hsr":
            return "mh"
        elif algo == "x17":
            return "mh"
        elif algo == "x11":
            return "gh"
        elif algo == "phi":
            return "mh"
        elif algo == "keccak":
            return "gh"
        elif algo == "sib":
            return "mh"
        elif algo == "qubit":
            return "gh"
        elif algo == "bitcore":
            return "mh"
        elif algo == "yescrypt":
            return "kh"
        elif algo == "x11evo":
            return "mh"
        elif algo == "c11":
            return "mh"
        elif algo == "veltor":
            return "mh"
        elif algo == "polytimos":
            return "mh"
        elif algo == "skunk":
            return "mh"
        elif algo == "nist5":
            return "mh"
        elif algo == "lyra2v2":
            return "mh"
        elif algo == "groestl":
            return "mh"
        elif algo == "tribus":
            return "mh"
        elif algo == "timetravel":
            return "mh"
        elif algo == "lbry":
            return "mh"
        elif algo == "skein":
            return "mh"
        elif algo == "x13":
            return "mh"
        elif algo == "myr-gr":
            return "mh"
        elif algo == "x14":
            return "mh"
        elif algo == "lyra2z":
            return "mh"
        else:
            raise Exception("Unsupported algo: %s" % algo)

    def _fetch_most_profitable_algo(self, supported_algos, algo_to_benchmarks):
        pr("Fetching currency info for pool...\n", prefix="Zpool Mining Group")
        data = Fetcher.fetch_json_api("http://www.zpool.ca/api/currencies")

        best_algo = None
        best_estimate = -1
        for v in data.values():
            if v["algo"] in supported_algos:
                profitability = algo_to_benchmarks[v["algo"]].get_24_hour_profitability(
                    float(v["estimate"]), self._get_zpool_profitability_unit(v["algo"]))
                if profitability > best_estimate:
                    best_algo = v["algo"]
                    best_estimate = profitability

        return best_algo

    def _fetch_pools(self):
        pr("Fetching pool info...\n", prefix="ZPool Mining Group")
        data = Fetcher.fetch_json_api("http://www.zpool.ca/api/status")

        return {
            v["name"]: {"algo": v["name"], "port": v["port"]}
            for v in data.values()
        }

    def _filter_blacklisted_algos_from_pools(self, algo_to_pool):
        algo_to_pool = dict(algo_to_pool)
        for algo in ZPoolMiningGroup.BLACKLISTED_ALGOS:
            del algo_to_pool[algo]

        return algo_to_pool

    def _generate_password(self, payout_currency):
        return "c=%s" % (payout_currency.upper())

    def _create_miners_based_on_pools(self, algo_to_pools):
        pr("Prepping pool miners...\n", prefix="Zpool Mining Group")
        miners = {}
        pool_algos = {p["algo"] for p in algo_to_pools.values()}

        # CCMiner
        supported_ccminer_algos = CCMiner.get_supported_algos() & pool_algos

        algo_to_custom_ccminer = {
            "lyra2v2": "/usr/local/bin/vertminer",
        }
        default_ccminer = "/usr/local/bin/ccminer"

        for algo in supported_ccminer_algos:
            path_to_exec = algo_to_custom_ccminer.get(algo) or default_ccminer
            url = "stratum+tcp://%s%s" % (algo, ZPoolMiningGroup.ZPOOL_URL_SUFFIX)
            port = algo_to_pools[algo]["port"]
            wallet = Wallets.get_wallet_for(self._payout_currency)
            password = self._generate_password(self._payout_currency)

            miners[algo] = CCMiner(path_to_exec, algo, url, port, wallet, password)

        return miners

    def _get_benchmarks(self, algo_to_miners):
        pr("Loading benchmarks from cache...\n", prefix="Zpool Mining Group")
        return {algo: miner.benchmark() for algo, miner in algo_to_miners.items()}

    def get_most_profitable_miner(self):
        algo_to_pools = self._fetch_pools()
        algo_to_pools = self._filter_blacklisted_algos_from_pools(algo_to_pools)
        algo_to_miners = self._create_miners_based_on_pools(algo_to_pools)
        algo_to_benchmarks = self._get_benchmarks(algo_to_miners)
        best_algo = self._fetch_most_profitable_algo(set(algo_to_miners.keys()), algo_to_benchmarks)

        return algo_to_miners[best_algo]

    def __str__(self):
        return "Zpool Mining Group"

from subprocess import PIPE, Popen

from multi_miner.miners.ccminer import CCMiner
from multi_miner.mining_groups.abstract_mining_group import AbstractMiningGroup
from multi_miner.misc.config_loader import InvalidMiningConfig, MiningConfigLoader
from multi_miner.misc.fetcher import Fetcher
from multi_miner.misc.logging import LOG


class ZPoolMiningGroupLoader(MiningConfigLoader):
    def describe(self):
        return "Looks like you're try to mine zpool!"

    def describe_payout_currency(self):
        return "Put the three letter acronym of the payout currency here."

    def parse_payout_currency(self, value):
        if len(value) == 3:
            return str(value)
        else:
            raise InvalidMiningConfig("This is probably a bad payout currency. Should be three letters.")


class ZPoolMiningGroup(AbstractMiningGroup):
    ZPOOL_URL_SUFFIX = ".mine.zpool.ca"
    BLACKLISTED_ALGOS = set(["scrypt"])

    @staticmethod
    def get_group_config_loader():
        return ZPoolMiningGroupLoader()

    @staticmethod
    def init_from_config(config):
        return ZPoolMiningGroup(config["payout_currency"], config["wallet"])

    def __init__(self, payout_currency, wallet):
        self._payout_currency = payout_currency
        self._wallet = wallet

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

    def _get_currencies(self):
        LOG.debug("Fetching currency info...")
        return list(Fetcher.fetch_json_api("http://www.zpool.ca/api/currencies").values())

    def _fetch_most_profitable_algo(self, currencies, algo_to_benchmarks):
        LOG.debug("Finding most profitable algo...")

        def _get_prof(c):
            return algo_to_benchmarks[c["algo"]].get_24_hour_profitability(
                float(c["estimate"]),
                self._get_zpool_profitability_unit(c["algo"]),
            )

        sorted_currencies = sorted(
            [c for c in currencies if c["algo"] in algo_to_benchmarks],
            key=_get_prof,
            reverse=True,
        )
        for v in sorted_currencies:
            LOG.debug("\tProfitability of %s (%s) = %0.4f", v["name"], v["algo"], _get_prof(v))

        return sorted_currencies[0]["algo"]

    def _filter_blacklisted_algos_from_currencies(self, currencies):
        return [c for c in currencies if c["algo"] not in ZPoolMiningGroup.BLACKLISTED_ALGOS]

    def _generate_password(self, payout_currency):
        return "c=%s" % (payout_currency.upper())

    def _create_miners_for_currencies(self, currencies):
        LOG.debug("Prepping miners...")
        miners = {}
        algo_to_port = {c["algo"]: c["port"] for c in currencies}
        supported_algos = set(algo_to_port.keys())

        # CCMiner
        supported_ccminer_algos = CCMiner.get_supported_algos() & supported_algos

        algo_to_custom_ccminer = {
            "lyra2v2": "/usr/local/bin/vertminer",
        }
        default_ccminer = "/usr/local/bin/ccminer"

        for algo in supported_ccminer_algos:
            path_to_exec = algo_to_custom_ccminer.get(algo) or default_ccminer
            url = "stratum+tcp://%s%s" % (algo, ZPoolMiningGroup.ZPOOL_URL_SUFFIX)
            port = algo_to_port[algo]
            password = self._generate_password(self._payout_currency)

            miners[algo] = CCMiner(path_to_exec, algo, url, port, self._wallet, password)

        return miners

    def _get_benchmarks(self, algo_to_miners):
        LOG.debug("Loading benchmarks from cache...")
        return {algo: miner.benchmark() for algo, miner in algo_to_miners.items()}

    def get_most_profitable_miner(self):
        currencies = self._get_currencies()
        currencies = self._filter_blacklisted_algos_from_currencies(currencies)
        algo_to_miners = self._create_miners_for_currencies(currencies)
        algo_to_benchmarks = self._get_benchmarks(algo_to_miners)
        best_algo = self._fetch_most_profitable_algo(currencies, algo_to_benchmarks)

        return algo_to_miners[best_algo]

    def __str__(self):
        return "Zpool Mining Group"

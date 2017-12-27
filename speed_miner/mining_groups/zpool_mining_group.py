from collections import namedtuple

from speed_miner.miners.ccminer import CCMiner
from speed_miner.mining_groups.abstract_mining_group import AbstractMiningGroup
from speed_miner.misc.config_loader import InvalidMiningConfig, MiningConfigLoader
from speed_miner.misc.fetcher import Fetcher
from speed_miner.misc.logging import LOG


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

    def describe_algo_blacklist(self):
        return "A list of algos to not mine. Separate each by a comma."

    def default_parse_algo_blacklist(self, value):
        if value is None:
            return set()
        return {v.lower().strip() for v in value.split(",")}

    def describe_algo_data_source(self):
        desc = "Put the desired zpool API with which to calculate profitability. Currently, it doesn't seem one API is best for maximizing profitability and there are only small differences in values between them. Possible values:\n"
        desc += "* \"algo\": This will query the API that gives estimates bucketed by algorithm. Currently, this seems to be the most stable API.\n"
        desc += "* \"currency\": This will query the API that gives estimates bucketed by currency. Currently, a less stable API."
        return desc

    def default_parse_algo_data_source(self, value):
        if value is None:
            return "algo"

        possible_values = {"algo", "currency"}

        if value not in possible_values:
            raise InvalidMiningConfig("%s is a bad algo data source." % value)

        return value

    def describe_calc_all_algo_data_sources(self):
        return "This can be \"true\" or \"false\". If \"true\", then we will calculate profitability from all data sources and print them out. This will not affect which data source gets used, this is merely to allow comparisons of different data sources."

    def default_parse_calc_all_algo_data_sources(self, value):
        if value is None:
            return False

        possible_values = {"true", "false"}

        value = value.lower().strip()
        if value not in possible_values:
            raise InvalidMiningConfig("%s is a bad value for \"calc_all_data_source\"." % value)

        return value == "true"


AlgoInfo = namedtuple("AlgoInfo", ["port", "algo", "prof_rate"])


class ZPoolMiningGroup(AbstractMiningGroup):
    ZPOOL_URL_SUFFIX = ".mine.zpool.ca"
    ALGO_BLACKLIST = set(["scrypt"])

    @staticmethod
    def get_group_config_loader():
        return ZPoolMiningGroupLoader()

    @staticmethod
    def init_from_config(config):
        return ZPoolMiningGroup(
            config["payout_currency"],
            config["wallet"],
            algo_data_source=config["algo_data_source"],
            calc_all_algo_data_sources=config["calc_all_algo_data_sources"],
            algo_blacklist=config["algo_blacklist"],
        )

    def __init__(self, payout_currency, wallet, algo_data_source="status", calc_all_algo_data_sources=False, algo_blacklist=None):
        self._payout_currency = payout_currency
        self._wallet = wallet
        self._algo_data_source = algo_data_source
        self._calc_all_algo_data_sources = calc_all_algo_data_sources
        self._algo_blacklist = (algo_blacklist or set()) | ZPoolMiningGroup.ALGO_BLACKLIST

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

    def _currency_to_algo_info(self, currencies):
        currencies = sorted(currencies, key=lambda c: float(c["estimate"]), reverse=True)
        algo_info_dict = {}

        for c in currencies:
            if c["algo"] not in algo_info_dict:
                algo_info_dict[c["algo"]] = AlgoInfo(algo=c["algo"], prof_rate=float(c["estimate"]), port=c["port"])

        return list(algo_info_dict.values())

    def _get_algo_info_from_currencies(self):
        LOG.debug("Fetching currency info...")
        return self._currency_to_algo_info(list(Fetcher.fetch_json_api("http://www.zpool.ca/api/currencies").values()))

    def _status_to_algo_info(self, statuses):
        return [
            AlgoInfo(algo=s["name"], prof_rate=float(s["estimate_current"]) * 1000.0, port=s["port"])
            for s in statuses
        ]

    def _get_algo_info_from_statuses(self):
        LOG.debug("Fetching algo statuses...")
        return self._status_to_algo_info(list(Fetcher.fetch_json_api("http://www.zpool.ca/api/status").values()))

    def _fetch_most_profitable_algo(self, algo_info, algo_to_benchmarks):
        def _get_prof(a):
            return algo_to_benchmarks[a.algo].get_24_hour_profitability(
                a.prof_rate,
                self._get_zpool_profitability_unit(a.algo),
            )

        sorted_algo_info = sorted(
            [a for a in algo_info if a.algo in algo_to_benchmarks],
            key=_get_prof,
            reverse=True,
        )
        for a in sorted_algo_info:
            LOG.debug("    Profitability of %s = %0.4f", a.algo, _get_prof(a))

        return sorted_algo_info[0].algo

    def _filter_blacklisted_algos_from_algo_info(self, algo_info):
        return [a for a in algo_info if a.algo not in self._algo_blacklist]

    def _generate_password(self, payout_currency):
        return "c=%s" % (payout_currency.upper())

    def _create_miners_for_algo_info(self, algo_info):
        LOG.debug("Prepping miners...")
        miners = {}
        algo_to_port = {a.algo: a.port for a in algo_info}
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

    def _get_most_profitable_miner_for_source(self, source):
        LOG.debug("Finding most profitable algo for source \"%s\"..." % source)
        if source == "algo":
            algo_info = self._get_algo_info_from_statuses()
        elif source == "currency":
            algo_info = self._get_algo_info_from_currencies()

        algo_info = self._filter_blacklisted_algos_from_algo_info(algo_info)
        algo_to_miners = self._create_miners_for_algo_info(algo_info)
        algo_to_benchmarks = self._get_benchmarks(algo_to_miners)
        best_algo = self._fetch_most_profitable_algo(algo_info, algo_to_benchmarks)
        return algo_to_miners[best_algo]

    def get_most_profitable_miner(self):
        if self._calc_all_algo_data_sources:
            other_source = "currency" if self._algo_data_source == "algo" else "algo"
            self._get_most_profitable_miner_for_source(other_source)

        return self._get_most_profitable_miner_for_source(self._algo_data_source)

    def __str__(self):
        return "Zpool Mining Group"

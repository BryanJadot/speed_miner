from speed_miner.mining_groups.multipool_mining_group import (
    AlgoInfo,
    MultipoolMiningGroup,
    MultipoolMiningGroupLoader,
)
from speed_miner.misc.config_loader import InvalidMiningConfig
from speed_miner.misc.fetcher import Fetcher
from speed_miner.misc.logging import LOG


class ZPoolMiningGroupLoader(MultipoolMiningGroupLoader):
    def describe(self):
        return "Looks like you're trying to mine zpool!"

    def describe_payout_currency(self):
        return "Put the three letter acronym of the payout currency here."

    def parse_payout_currency(self, value):
        if len(value) == 3:
            return str(value).upper()
        else:
            raise InvalidMiningConfig(
                "This is probably a bad payout currency. Should be three letters."
            )

    def describe_algo_data_source(self):
        desc = "Put the desired zpool API with which to calculate profitability. "
        desc += "Currently, it doesn't seem one API is best for maximizing profitability and "
        desc += "there are only small differences in values between them. Possible values:\n"
        desc += "* \"algo\": This will query the API that gives estimates bucketed by algorithm. "
        desc += "Currently, this seems to be the most stable API.\n"
        desc += "* \"currency\": This will query the API that gives estimates bucketed by "
        desc += "currency. Currently, a less stable API."
        return ("algo", desc)

    def default_parse_algo_data_source(self, value):
        if value is None:
            return "algo"

        possible_values = {"algo", "currency"}

        if value not in possible_values:
            raise InvalidMiningConfig("%s is a bad algo data source." % value)

        return value

    def describe_calc_all_algo_data_sources(self):
        desc = "This can be \"true\" or \"false\". If \"true\", then we will calculate "
        desc += "profitability from all data sources and print them out. This will not "
        desc += "affect which data source gets used, this is merely to allow "
        desc += "comparisons of different data sources."

        return ("false", desc)

    def default_parse_calc_all_algo_data_sources(self, value):
        if value is None:
            return False

        possible_values = {"true", "false"}

        value = value.lower().strip()
        if value not in possible_values:
            raise InvalidMiningConfig("%s is a bad value for \"calc_all_data_source\"." % value)

        return value == "true"


class ZPoolMiningGroup(MultipoolMiningGroup):
    ZPOOL_URL_SUFFIX = ".mine.zpool.ca"

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

    def __init__(
            self,
            payout_currency,
            wallet,
            algo_data_source="algo",
            calc_all_algo_data_sources=False,
            algo_blacklist=None):
        super().__init__(wallet, algo_blacklist=algo_blacklist)
        self._payout_currency = payout_currency
        self._algo_data_source = algo_data_source
        self._calc_all_algo_data_sources = calc_all_algo_data_sources

    def get_most_profitable_miner(self):
        if self._calc_all_algo_data_sources:
            curr_src = self._algo_data_source
            other_src = "currency" if curr_src == "algo" else "algo"
            LOG.debug("Switching to source \"%s\"..." % other_src)
            self._algo_data_source = other_src
            super().get_most_profitable_miner()
            LOG.debug("Reverting to source \"%s\"..." % curr_src)
            self._algo_data_source = curr_src

        return super().get_most_profitable_miner()

    def _get_algo_info(self):
        if self._algo_data_source == "algo":
            return self._get_algo_info_from_algos()
        elif self._algo_data_source == "currency":
            return self._get_algo_info_from_currencies()

    def _generate_password(self, algo):
        diff = ""
        # REMOVE THIS
        if algo == "skein":
            diff = ",d=2"
        elif algo == "timetravel":
            diff = ",d=5"
        return "c=%s%s" % (self._payout_currency.upper(), diff)

    def _get_zpool_profitability_unit(self, algo):
        if algo == "sha256":
            return "PH"
        elif algo == "scrypt":
            return "GH"
        elif algo == "equihash":
            return "ksol"
        elif algo == "neoscrypt":
            return "MH"
        elif algo == "m7m":
            return "MH"
        elif algo == "quark":
            return "GH"
        elif algo == "blake2s":
            return "GH"
        elif algo == "blakecoin":
            return "GH"
        elif algo == "xevan":
            return "MH"
        elif algo == "decred":
            return "GH"
        elif algo == "hsr":
            return "MH"
        elif algo == "x17":
            return "MH"
        elif algo == "x11":
            return "GH"
        elif algo == "phi":
            return "MH"
        elif algo == "keccak":
            return "GH"
        elif algo == "sib":
            return "MH"
        elif algo == "qubit":
            return "GH"
        elif algo == "bitcore":
            return "MH"
        elif algo == "yescrypt":
            return "Kh"
        elif algo == "x11evo":
            return "MH"
        elif algo == "c11":
            return "MH"
        elif algo == "veltor":
            return "MH"
        elif algo == "polytimos":
            return "MH"
        elif algo == "skunk":
            return "MH"
        elif algo == "nist5":
            return "MH"
        elif algo == "lyra2v2":
            return "MH"
        elif algo == "groestl":
            return "MH"
        elif algo == "tribus":
            return "MH"
        elif algo == "timetravel":
            return "MH"
        elif algo == "lbry":
            return "MH"
        elif algo == "skein":
            return "MH"
        elif algo == "x13":
            return "MH"
        elif algo == "myr-gr":
            return "MH"
        elif algo == "x14":
            return "MH"
        elif algo == "lyra2z":
            return "MH"
        else:
            raise Exception("Unsupported algo: %s" % algo)

    def _get_prof_str(self, estimate, algo):
        return "%s mbtc/%s*s/day" % (estimate, self._get_zpool_profitability_unit(algo))

    def _get_url(self, algo):
        return "stratum+tcp://%s%s" % (algo, ZPoolMiningGroup.ZPOOL_URL_SUFFIX)

    def _currency_to_algo_info(self, currencies):
        currencies = sorted(currencies, key=lambda c: float(c["estimate"]), reverse=True)
        algo_info_dict = {}

        for c in currencies:
            if c["algo"] not in algo_info_dict:
                algo_info_dict[c["algo"]] = AlgoInfo(
                    algo=c["algo"],
                    prof_str=self._get_prof_str(c["estimate"], c["algo"]),
                    port=c["port"],
                    url=self._get_url(c["algo"]),
                )

        return list(algo_info_dict.values())

    def _get_algo_info_from_currencies(self):
        LOG.debug("Fetching currency info...")
        return self._currency_to_algo_info(
            list(Fetcher.fetch_json_api("http://www.zpool.ca/api/currencies").values()))

    def _status_to_algo_info(self, statuses):
        return [
            AlgoInfo(
                algo=s["name"],
                prof_str=self._get_prof_str(float(s["estimate_current"]) * 1000.0, s["name"]),
                port=s["port"],
                url=self._get_url(s["name"]),
            )
            for s in statuses
        ]

    def _get_algo_info_from_algos(self):
        LOG.debug("Fetching algo info...")
        return self._status_to_algo_info(
            list(Fetcher.fetch_json_api("http://www.zpool.ca/api/status").values()))

    def __str__(self):
        return "Zpool Mining Group"

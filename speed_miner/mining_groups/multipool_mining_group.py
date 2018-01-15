from abc import abstractmethod
from collections import namedtuple

from speed_miner.miners import get_supported_algos, get_miner_for_algo
from speed_miner.mining_groups.abstract_mining_group import AbstractMiningGroup
from speed_miner.misc.config_loader import MiningConfigLoader
from speed_miner.misc.logging import LOG


class MultipoolMiningGroupLoader(MiningConfigLoader):

    def describe_algo_blacklist(self):
        return ("", "A list of algos to not mine. Separate each by a comma.")

    def default_parse_algo_blacklist(self, value):
        if value is None:
            return set()
        return {v.lower().strip() for v in value.split(",")}


AlgoInfo = namedtuple("AlgoInfo", ["url", "port", "algo", "prof_str"])


class MultipoolMiningGroup(AbstractMiningGroup):

    def __init__(self, wallet, algo_blacklist=None):
        self._wallet = wallet
        self._algo_blacklist = algo_blacklist or set()

    def get_most_profitable_miner(self):
        LOG.debug("Finding most profitable algo...")
        algo_info = self._get_algo_info()
        algo_info = self._filter_blacklisted_algos_from_algo_info(algo_info)
        algo_to_miners = self._create_miners_for_algo_info(algo_info)
        algo_to_benchmarks = self._get_benchmarks(algo_to_miners)
        best_algo = self._get_most_profitable_algo(algo_info, algo_to_benchmarks)
        return algo_to_miners[best_algo]

    @abstractmethod
    def _get_algo_info(self):
        pass

    @abstractmethod
    def _generate_password(self, algo):
        pass

    def _get_most_profitable_algo(self, algo_info, algo_to_benchmarks):
        def _get_prof(a):
            return algo_to_benchmarks[a.algo].get_mbtc_per_day(a.prof_str)

        sorted_algo_info = sorted(
            [a for a in algo_info if a.algo in algo_to_benchmarks],
            key=_get_prof,
            reverse=True,
        )
        for a in sorted_algo_info:
            LOG.debug("    Profitability of %s = %s mBTC / day", a.algo, _get_prof(a))

        return sorted_algo_info[0].algo

    def _filter_blacklisted_algos_from_algo_info(self, algo_info):
        return [a for a in algo_info if a.algo not in self._algo_blacklist]

    def _create_miners_for_algo_info(self, algo_info):
        LOG.debug("Prepping miners...")
        miners = {}
        algo_to_info = {a.algo: a for a in algo_info}
        supported_algos = get_supported_algos() & set(algo_to_info.keys())

        for algo in supported_algos:
            url = algo_to_info[algo].url
            port = algo_to_info[algo].port
            password = self._generate_password(algo)

            miners[algo] = get_miner_for_algo(algo, url, port, self._wallet, password)

        return miners

    def _get_benchmarks(self, algo_to_miners):
        LOG.debug("Loading benchmarks from cache...")
        return {algo: miner.benchmark() for algo, miner in algo_to_miners.items()}

from requests import get as rget
from requests.exceptions import ReadTimeout

from time import sleep

from speed_miner.misc.logging import LOG


class Fetcher(object):
    _cache = {}
    _MAX_WAIT = 120
    _TIMEOUT = 5

    @staticmethod
    def fetch_json_api(url, use_cache_on_failure=False):
        num_tries = 0
        while True:
            resp_json = Fetcher._try_fetching_resp(url)

            if resp_json:
                Fetcher._cache[url] = resp_json
                return resp_json
            elif use_cache_on_failure and url in Fetcher._cache:
                LOG.warn("Bad response from '%s\'! Falling back to cache...\033[0m\n", url)
                return Fetcher._cache[url]

            num_tries += 1
            sleep_time = min(2**num_tries - 1, Fetcher._MAX_WAIT)
            LOG.warning("Bad response from '%s\'! Backing off for %i second(s)...", url, sleep_time)
            sleep(sleep_time)

    @staticmethod
    def _try_fetching_resp(url):
        try:
            resp = rget(url, timeout=Fetcher._TIMEOUT)
        except ReadTimeout as e:
            return None

        if resp.status_code != 200:
            return None

        try:
            return resp.json()
        except ValueError:
            return None

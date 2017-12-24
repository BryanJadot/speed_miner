import sys

from requests import get as rget
from requests.exceptions import ReadTimeout

from time import sleep

from multi_miner.misc.logger import pr

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
                pr(
                    "\033[91mBad response from '%s\'! Falling back to cache...\033[0m\n" % url,
                    prefix="Fetcher",
                    stream=sys.stderr,
                )
                return Fetcher._cache[url]

            num_tries += 1
            sleep_time = min(2**num_tries - 1, Fetcher._MAX_WAIT)
            pr(
                "\033[91mBad response from '%s\'! Backing off for %i second(s)...\033[0m\n" % (url, sleep_time),
                prefix="Fetcher",
                stream=sys.stderr,
            )
            sleep(sleep_time)

    @staticmethod
    def _try_fetching_resp(url):
        try:
            resp = rget(url, timeout=Fetcher._TIMEOUT)
        except ReadTimeout as err:
            return None

        if resp.status_code != 200:
            return None

        try:
            return resp.json()
        except ValueError as err:
            return None

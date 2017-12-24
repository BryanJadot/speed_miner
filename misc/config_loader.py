from abc import ABC, abstractmethod

from json import loads
from json.decoder import JSONDecodeError

from sys import stderr

from multi_miner.misc.logger import pr


class InvalidMiningConfig(Exception):
    pass


class MiningConfigManager(object):
    def __init__(self):
        self._config = {}

    def load_from_json_dict(self, loader, json_dict):
        self._config.update(loader.process_config_from_dict(json_dict))

    def load_from_file(self, loader, filename):
        self._config.update(loader.process_config_from_file(filename))

    def get_config(self):
        return self._config


def _catch_invalid_config(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except InvalidMiningConfig as err:
            self._print_error(err)
            exit(1)

    return wrapper


class MiningConfigLoader(ABC):
    @_catch_invalid_config
    def process_config_from_file(self, filename):
        try:
            json_dict = loads(open(filename, "r").read())
        except JSONDecodeError as err:
            raise InvalidMiningConfig("Config file is not JSON formatted")

        return self.process_config_from_dict(json_dict)

    def _get_prefix_funcs(self, prefix):
        # Get a map dict where the values are functions starting with a specified prefix
        # and the keys are the names of the functions, with the prefix snipped off.
        #
        # Ex: if a class contains the functions 'parse_group' and 'parse_coin', this will
        # return {'group': parse_group, 'coin': parse_coin}.
        return {
            func[len(prefix):]: getattr(self, func) for func in dir(self)
            if callable(getattr(self, func)) and func.startswith(prefix)
        }

    @_catch_invalid_config
    def process_config_from_dict(self, json_dict):
        parse_funcs = self._get_prefix_funcs("parse_")
        missing_keys = set(parse_funcs.keys()) - set(json_dict.keys())
        if len(missing_keys) > 0:
            raise InvalidMiningConfig("Missing required config parameter(s) - %s" % ", ".join(missing_keys))

        return {
            k: func(json_dict[k])
            for k, func in parse_funcs.items()
        }

    def _print_error(self, err):
        pr("\033[31mError occurred: \"%s\".\033[m\n\n" % str(err), stream=stderr)

        pr("%s\nPossible parameters:\n" % self.describe(), stream=stderr)

        cmd_to_description = self._get_prefix_funcs("describe_")
        for cmd, desc_func in cmd_to_description.items():
            string = "\n\033[1m%s\033[0m\n\t%s\n" % (cmd, desc_func().replace("\n", "\n\t"))
            pr(string, stream=stderr)
        pr("\n", stream=stderr)

    @abstractmethod
    def describe(self):
        pass

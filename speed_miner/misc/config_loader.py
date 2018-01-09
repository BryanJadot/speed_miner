import sys

from abc import ABC, ABCMeta, abstractmethod

from json import loads
from json.decoder import JSONDecodeError


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


class MiningConfigLoaderMeta(ABCMeta):

    def __init__(cls, name, bases, dct):
        super(MiningConfigLoaderMeta, cls).__init__(name, bases, dct)
        desc_funcs = cls._get_prefix_funcs("describe_")
        parse_funcs = cls._get_prefix_funcs("parse_")
        default_parse_funcs = cls._get_prefix_funcs("default_parse_")

        descs = set(desc_funcs.keys())
        parses = set(parse_funcs.keys()) | set(default_parse_funcs.keys())

        assert descs - parses == set(), \
            "Missing parse function(s) for params: %s" % ", ".join(descs - parses)
        assert parses - descs == set(), \
            "Missing describe function(s) for params: %s" % ", ".join(parses - descs)


class MiningConfigLoader(ABC, metaclass=MiningConfigLoaderMeta):

    @classmethod
    def _get_prefix_funcs(cls, prefix):
        # Get a map dict where the values are functions starting with a specified prefix
        # and the keys are the names of the functions, with the prefix snipped off.
        #
        # Ex: if a class contains the functions 'parse_group' and 'parse_coin', this will
        # return {'group': parse_group, 'coin': parse_coin}.
        return {
            func[len(prefix):]: getattr(cls, func) for func in dir(cls)
            if callable(getattr(cls, func)) and func.startswith(prefix)
        }

    @_catch_invalid_config
    def process_config_from_file(self, filename):
        try:
            json_dict = loads(open(filename, "r").read())
        except JSONDecodeError as err:
            raise InvalidMiningConfig("Config file is not JSON formatted")

        return self.process_config_from_dict(json_dict)

    @_catch_invalid_config
    def process_config_from_dict(self, json_dict):
        parse_funcs = self._get_prefix_funcs("parse_")
        missing_keys = set(parse_funcs.keys()) - set(json_dict.keys())
        if len(missing_keys) > 0:
            raise InvalidMiningConfig(
                "Missing required config parameter(s) - %s" % ", ".join(missing_keys))

        parse_funcs.update(self._get_prefix_funcs("default_parse_"))
        return {
            k: func(self, json_dict.get(k))
            for k, func in parse_funcs.items()
        }

    def _print_error(self, err):
        err_str = ("\033[31mError occurred: \"%s\".\033[m\n\n" % str(err))
        err_str += ("%s\nPossible parameters:\n" % self.describe())

        parse_params = sorted(list(self._get_prefix_funcs("parse_").keys()))
        default_funcs = self._get_prefix_funcs("default_parse_")
        default_parse_params = sorted(list(default_funcs.keys()))

        param_to_description = self._get_prefix_funcs("describe_")
        for param in parse_params:
            desc_func = param_to_description[param]
            err_str += "\n\033[1m%s\033[0m\n\t%s\n" % (param, desc_func(self).replace("\n", "\n\t"))

        for param in default_parse_params:
            desc_func = param_to_description[param]
            err_str += "\n\033[1m%s (default: \"%s\")\033[0m\n\t%s\n" % (
                param,
                default_funcs[param](self, None),
                desc_func(self).replace("\n", "\n\t"),
            )

        err_str += "\n"
        print(err_str, file=sys.stderr)

    @abstractmethod
    def describe(self):
        pass

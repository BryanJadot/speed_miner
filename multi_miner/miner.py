import logging

from argparse import ArgumentParser

from multi_miner.monitor import MiningMonitor
from multi_miner.mining_groups.zpool_mining_group import ZPoolMiningGroup
from multi_miner.misc.config_loader import (
    InvalidMiningConfig,
    MiningConfigLoader,
    MiningConfigManager,
)
from multi_miner.misc.logging import LOG


class MainConfigLoader(MiningConfigLoader):
    def describe(self):
        return "Let's mine some coin! Please view README.md for more information on how to set up this program."

    def describe_group(self):
        return "Possible values:\n* \"zpool\": This group will multimine zpool.ca"

    def parse_group(self, value):
        if value == "zpool":
            return ZPoolMiningGroup
        else:
            raise InvalidMiningConfig("%s is not a valid group value" % value)

    def describe_wallet(self):
        return "Put your wallet address here."

    def parse_wallet(self, value):
        return str(value)

    def describe_log_level(self, value):
        log_desc = "Define a lower threshold of log values to output. Logs of a level below this value will not be outputed. Possible values in ascending order:\n"
        log_desc += "* \"DEBUG\": This level show all output values. Noisy but informative.\n"
        log_desc += "* \"INFO\": Show high-level information about the operation of the program.\n"
        log_desc += "* \"WARNING\": Show warnings. These will be logs warning of potential problems that may occur, but haven't affected operation of the program.\n"
        log_desc += "* \"ERROR\": Show errors. These are issues that prevented some functionality of the program.\n"
        log_desc += "* \"CRITICAL\": Show critical and worse errors. These are issues that prevented the program from continuing."

    def default_parse_log_level(self, value):
        # If one wasn't specied, return a default value.
        if value is None:
            return log_levels["info"]

        parsed_val = LOG.all_log_levels.get(value.lower())

        # If the provided value wasn't what was expected
        if parsed_val is None:
            raise InvalidMiningConfig("%s is not a valid log level." % value)

        return parsed_val


def mine():
    parser = ArgumentParser()
    parser.add_argument(
        "-c",
        type=str,
        dest="config_path",
        help="Specify the path to your mining config file as CONFIG_PATH.",
        required=True,
    )
    args = parser.parse_args()

    config_man = MiningConfigManager()

    main_config_loader = MainConfigLoader()
    config_man.load_from_file(main_config_loader, args.config_path)

    LOG.init_logging(config_man.get_config()["log_level"])

    mining_group_cls = config_man.get_config()["group"]
    group_config_loader = mining_group_cls.get_group_config_loader()
    config_man.load_from_file(group_config_loader, args.config_path)

    config = config_man.get_config()
    MiningMonitor.mine(mining_group_cls.init_from_config(config))

import atexit
import os
import signal
import sys

from argparse import ArgumentParser

from speed_miner.monitor import MiningMonitor
from speed_miner.mining_groups.nicehash_mining_group import NicehashMiningGroup
from speed_miner.mining_groups.zpool_mining_group import ZPoolMiningGroup
from speed_miner.misc.config_loader import (
    InvalidMiningConfig,
    MiningConfigLoader,
    MiningConfigManager,
)
from speed_miner.misc.logging import LOG
from speed_miner.misc.process_util import term_all_procs


class MinerConfigLoader(MiningConfigLoader):
    def describe(self):
        desc = "Let's mine some coin! Please view README.md for more information on how to set up "
        desc += "this program."
        return desc

    def describe_group(self):
        return "Possible values:\n* \"zpool\": This group will multimine zpool.ca"

    def parse_group(self, value):
        if value == "zpool":
            return ZPoolMiningGroup
        elif value == "nicehash":
            return NicehashMiningGroup
        else:
            raise InvalidMiningConfig("%s is not a valid group value" % value)

    def describe_wallet(self):
        return "Put your wallet address here."

    def parse_wallet(self, value):
        return str(value)

    def describe_log_level(self):
        log_desc = "Define a lower threshold of log values to output. "
        log_desc += "Logs of a level below this value will not be outputed. "
        log_desc += "Possible values in ascending order:\n"
        log_desc += "* \"DEBUG\": This level show all output values. Noisy but informative.\n"
        log_desc += "* \"INFO\": Show high-level information about the operation of the program.\n"
        log_desc += "* \"WARNING\": Show warnings. These will be logs warning of potential "
        log_desc += "problems that may occur, but haven't affected operation of the program.\n"
        log_desc += "* \"ERROR\": Show errors. These are issues that prevented some functionality "
        log_desc += "of the program.\n"
        log_desc += "* \"CRITICAL\": Show critical and worse errors. These are issues that "
        log_desc += "prevented the program from continuing."

        return ("INFO", log_desc)

    def default_parse_log_level(self, value):
        # If one wasn't specied, return a default value.
        if value is None:
            return LOG.all_log_levels["info"]

        parsed_val = LOG.all_log_levels.get(value.lower())

        # If the provided value wasn't what was expected
        if parsed_val is None:
            raise InvalidMiningConfig("%s is not a valid log level" % value)

        return parsed_val


def _parse_args_and_start_mining():
    _init_exit_handling()
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

    main_config_loader = MinerConfigLoader()
    config_man.load_from_file(main_config_loader, args.config_path)
    LOG.set_level(config_man.get_config()["log_level"])

    mining_group_cls = config_man.get_config()["group"]
    group_config_loader = mining_group_cls.get_group_config_loader()
    config_man.load_from_file(group_config_loader, args.config_path)

    config = config_man.get_config()
    MiningMonitor.mine(mining_group_cls.init_from_config(config))


def _signal_handler(signum, frame):
    LOG.debug('Signal handler called with signal %i', signum)
    term_all_procs()
    os._exit(128 + signum)


def _init_exit_handling():
    atexit.register(term_all_procs)
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)
    signal.signal(signal.SIGQUIT, _signal_handler)


def start():
    try:
        _parse_args_and_start_mining()
    except SystemExit as ex:
        raise ex
    except Exception:
        LOG.exception("Uncaught exception caused a program crash!")
        LOG.debug("Exiting...")
        sys.exit(1)

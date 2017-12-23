#!/usr/bin/python3

SRC_LOC = '/usr/local/src'

from argparse import ArgumentParser
import sys
sys.path.insert(0, SRC_LOC)
sys.path.insert(0, "/home/bryan/src")

from subprocess import Popen

from multi_miner.monitor import MiningMonitor
from multi_miner.mining_groups.zpool_mining_group import ZPoolMiningGroup
from multi_miner.misc.config_loader import (
    InvalidMiningConfig,
    MiningConfigLoader,
    MiningConfigManager,
)


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


if __name__ == "__main__":
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

    mining_group_cls = config_man.get_config()["group"]
    group_config_loader = mining_group_cls.get_group_config_loader()
    config_man.load_from_file(group_config_loader, args.config_path)

    config = config_man.get_config()
    MiningMonitor.mine(mining_group_cls.init_from_config(config))

#!/usr/bin/python3
import sys
sys.path.insert(0, '/home/bryan/src')

from multi_miner.monitor import MiningMonitor
from multi_miner.mining_groups.zpool_mining_group import ZPoolMiningGroup()

if __name__ == "main":
    MiningMonitor.mine(ZPoolMiningGroup())

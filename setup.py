#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name="SpeedMiner",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'miner = multi_miner.miner:mine',
        ]
    }
)

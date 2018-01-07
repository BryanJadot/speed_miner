from setuptools import setup, find_packages
setup(
    name="SpeedMiner",
    version="0.1",
    packages=find_packages(exclude=["tests"]),
    test_suite="tests",
    entry_points={
        'console_scripts': [
            'miner = speed_miner.miner:start',
        ]
    }
)

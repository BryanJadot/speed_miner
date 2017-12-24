from abc import ABC, abstractmethod

class AbstractMiningGroup(ABC):
    @staticmethod
    @abstractmethod
    def get_group_config_loader():
        pass

    @staticmethod
    @abstractmethod
    def init_from_config(config):
        pass

    @abstractmethod
    def get_most_profitable_miner(self):
        pass

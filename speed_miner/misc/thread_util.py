import os

from threading import Thread

from speed_miner.monitor import MiningMonitor
from speed_miner.misc.logging import LOG

class CrashThread(Thread):
    def run(self):
        try:
            super().run()
        except:
            LOG.exception("Thread %s crashed. Crashing program...", self.name)
            MiningMonitor.mark_monitor_for_exit(1)

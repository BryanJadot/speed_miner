from threading import Thread

from speed_miner.monitor import MiningMonitor
from speed_miner.misc.logging import LOG


class CrashThread(Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dameon = True

    def run(self):
        try:
            super().run()
        except Exception:
            LOG.exception("Thread %s crashed. Crashing program...", self.name)
            MiningMonitor.mark_monitor_for_exit(1)

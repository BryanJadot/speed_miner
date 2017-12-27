import os

from threading import Thread

from multi_miner.misc.logging import LOG

class CrashThread(Thread):
    def run(self):
        try:
            super().run()
        except:
            LOG.exception("Thread %s crashed. Crashing program...", self.name)
            os._exit(1)

import logging

from unittest import TestCase


class MinerTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        logging.getLogger().setLevel(logging.WARNING)

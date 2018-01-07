import inspect
import logging
import sys


class _LogRangeFilter(logging.Filter):
    def __init__(self, low, high):
        self._low = low
        self._high = high

    def filter(self, record):
        return record.levelno >= self._low and record.levelno <= self._high


class _MinerFormatter(logging.Formatter):
    def _get_log_color(self, log_level):
        return {
            logging.DEBUG: "\033[0m",
            logging.INFO: "\033[94m",
            logging.WARNING: "\033[93m",
            logging.ERROR: "\033[91m",
            logging.CRITICAL: "\033[91m",
        }[log_level] + "\033[1m"

    def usesTime(self):
        return True

    def formatMessage(self, record):
        record_dict = record.__dict__
        record_dict.update({"color_fmt": self._get_log_color(record.levelno)})
        return "%(color_fmt)s[%(asctime)s - %(levelname)s]\033[0m %(message)s" % record_dict


class _LOGMeta(type):
    def __init__(cls, name, bases, dct):
        cls._total_shares = 0
        cls._total_accepts = 0
        cls.all_log_levels = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL,
        }

        cls._init_logging()

    def _init_logging(cls):
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)
        cls._setup_logger(logging.getLogger())

    def _setup_logger(cls, logger):
        stdout_handler = logging.StreamHandler(stream=sys.stdout)
        stdout_handler.addFilter(_LogRangeFilter(logging.DEBUG, logging.INFO))
        stdout_handler.setFormatter(_MinerFormatter())
        stdout_handler.setLevel(logging.DEBUG)

        stderr_handler = logging.StreamHandler(stream=sys.stderr)
        stderr_handler.addFilter(_LogRangeFilter(logging.WARNING, logging.CRITICAL))
        stderr_handler.setFormatter(_MinerFormatter())
        stderr_handler.setLevel(logging.DEBUG)

        # Temporarily set output to DEBUG
        logger.setLevel(logging.DEBUG)
        logger.addHandler(stdout_handler)
        logger.addHandler(stderr_handler)

        return logger

    def set_level(cls, log_level):
        logging.getLogger().setLevel(log_level)

    def share(cls, algo, was_accepted, hashrate):
        cls._total_shares += 1
        accept_text = "\033[91mrejected\033[0m"
        if was_accepted:
            cls._total_accepts += 1
            accept_text = "\033[92maccepted\033[0m"

        str_replacements = (algo, accept_text, hashrate, cls._total_accepts, cls._total_shares)
        cls.info("Share of %s %s @ %s (%i/%i)" % str_replacements)

    def __getattr__(cls, key):
        # For now, lock down non-logging functions.
        if key not in cls.all_log_levels and key != "exception":
            raise AttributeError(key)

        return getattr(cls._get_logger(), key)

    def _get_logger(cls):
        stack = inspect.stack()
        name = inspect.getmodule(stack[2][0]).__name__
        logger = logging.getLogger(name)

        return logger


class LOG(object, metaclass=_LOGMeta):
    pass

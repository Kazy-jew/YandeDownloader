#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
logger.py
Ayase
logger
10/13/2022 7:37 PM
YandeDownloader
Oct
utils
2022 10 13 19 37 11
"""

import logging
import logging.config
from src.settings import LOG_DIR


def filter_maker(level):
    level = getattr(logging, level)

    def filter_(record):
        return record.levelno < level

    return filter_


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s, [%(name)s]: %(pathname)s, line %(lineno)d %(funcName)s: [%(levelname)s] %(message)s",
            "datefmt": "%m/%d/%Y %I:%M:%S %p"
        },
        "simple": {
            "format": "%(message)s"
        }
    },
    "filters": {
        "warning_and_below": {
            "()": filter_maker,
            "level": "ERROR"
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
            "filters": ["warning_and_below"]
        },
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "ERROR",
            "formatter": "simple",
            "stream": "ext://sys.stderr"
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": "log.log",
            "mode": "a"
        },
        "fileinfo": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "verbose",
            "filename": "log.log",
            "mode": "a"
        },
        "info": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "INFO",
            "formatter": "verbose",
            "when": "W0",
            "backupCount": 7,
            "filename": "app.log"
        },
        "debug": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "level": "DEBUG",
            "formatter": "verbose",
            "when": "midnight",
            "backupCount": 7,
            "filename": "app.log"
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": [
            "stderr",
            "stdout",
            "info",
            "debug"
        ]
    }
}


def my_logger(name):
    if not LOG_DIR.exists():
        LOG_DIR.mkdir(parents=True)
    LOG_CONFIG["handlers"]["debug"]["filename"] = LOG_DIR / 'app.log'
    LOG_CONFIG["handlers"]["info"]["filename"] = LOG_DIR / 'app.info.log'
    logging.config.dictConfig(LOG_CONFIG)
    my_log = logging.getLogger(name)
    return my_log


# logger = my_logger("my")
#
# logger.debug('This message should go to the log file')
# logger.info('So should this')
# logger.warning('And this, too')
# logger.error('And non-ASCII stuff, too, like 日啊')
# logger.info(f"{getattr(logging, 'info'.upper(), None)}")
# try:
#     1/0
# except Exception as e:
#     logger.exception(e)

if __name__ == '__main__':
    pass

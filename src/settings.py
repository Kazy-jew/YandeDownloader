#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
file name    :settings.py
author       :Ayase
created at   :10/14/2022 8:53 PM
project      :YandeDownloader
description  :global variables definition
"""

import sys
from pathlib import Path

ROOT_DIR = Path(sys.path[1])
LOG_DIR = ROOT_DIR / '.log'
DRIVER_DIR = ROOT_DIR / 'drivers'
STATUS_CONFIG_DIR = ROOT_DIR / 'conf/conf.d'
ASSET_DIR = ROOT_DIR / 'assets'
CACHE_DIR = ROOT_DIR / 'assets/.cache'
UPDATE_DIR = ROOT_DIR / 'assets/.update'
DATA_DIR = ROOT_DIR / 'assets/data'
JSON_DATA = DATA_DIR / 'json'
TEXT_DATA = DATA_DIR / 'txt'

CHROME = 'chromedriver'
FIREFOX = 'geckodriver'
OPERA = 'operadriver'

CONFIG_PATH = ROOT_DIR / 'conf/site.ini'
DRIVER_CHROME_PATH = ''
DRIVER_FIREFOX_PATH = ''
DRIVER_OPERA_PATH = ''

if sys.platform == 'win32':
    DRIVER_CHROME_PATH = DRIVER_DIR / f'{CHROME}.exe'
    DRIVER_FIREFOX_PATH = DRIVER_DIR / f'{FIREFOX}.exe'
    DRIVER_OPERA_PATH = DRIVER_DIR / f'{OPERA}.exe'
else:
    DRIVER_CHROME_PATH = DRIVER_DIR / CHROME
    DRIVER_FIREFOX_PATH = DRIVER_DIR / FIREFOX
    DRIVER_OPERA_PATH = DRIVER_DIR / OPERA


# image json info
class ImageData:
    imgData = {}


if __name__ == "__main__":
    print(ROOT_DIR, LOG_DIR, DRIVER_OPERA_PATH)

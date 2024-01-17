#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Notice:
# browser other than Google Chrome is not got fully tested yet
# so better not to use
"""
file name:    browser.py
author:       Ayase
created at:   10/15/2022 1:47 AM
project:      YandeDownloader
"""
import logging
import sys
import os

from pathlib import Path

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
# from webdriver_manager.opera import OperaDriverManager
from selenium.webdriver.chrome.service import Service as chromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
# from selenium.webdriver.opera.options import Options as operaOptions
from selenium.webdriver.remote.remote_connection import LOGGER

from src.utils.confparser import attribution
from src.settings import DRIVER_DIR, LOG_DIR

os.environ['WDM_LOCAL'] = '1'
os.environ['WDM_LOG'] = str(logging.NOTSET)
LOGGER.setLevel(logging.CRITICAL)


class _Base:
    def __init__(self, browser):
        self.name = browser

    def browser_options(self):
        match self.name:
            case 'chrome':
                return chromeService()
            case 'firefox':
                return FirefoxOptions()
            # case 'opera':
            #     return operaOptions()
            case _:
                raise ValueError('Browser not recognized')

    def browser_driver(self, options, manager=True, **kwargs):
        match self.name:
            case 'chrome':
                if manager:
                    return webdriver.Chrome(ChromeDriverManager().install(), options=options, **kwargs)
                return webdriver.Chrome(options=options, executable_path=DRIVER_DIR / 'chromedriver.exe', **kwargs)
            case 'firefox':
                if manager:
                    return webdriver.Firefox(options=options, service=FirefoxService(GeckoDriverManager().install(), service_log_path=None, log_output=None))
                return webdriver.Firefox(options=options, executable_path=DRIVER_DIR / 'geckodriver.exe',
                                         service_log_path=LOG_DIR / 'gecko.log', **kwargs)
            # case 'opera':
            #     return webdriver.Opera(options=options, executable_path=DRIVER_OPERA_PATH, **kwargs)
            case _:
                raise ValueError('Browser not recognized')


@attribution
class Browser(_Base):
    """
    @DynamicAttrs
    """
    def __init__(self, browser):
        super().__init__(browser)
        self.home = Path.home()
        if sys.platform == 'win32':
            self.profile = self.winprofile
            self.execution = self.winexec
        else:
            self.profile = self.posixprofile
            self.execution = self.posixexec

    def browser(self, location: str, binary_location: str = None):
        """
        instantiate a browser driver
        :param binary_location: location of the browser binary program
        :param location: download directory
        :return:
        """
        profile = self.home / self.profile
        option_ = self.browser_options()
        # change to your own browser profile path if is not installed with default configuration,
        # for chrome browser you can find it under address chrome://version/
        # for opera is opera:about (opera:flags for advanced config)
        prefs = {'download.default_directory': location}
        # keep browser open
        if self.name in ['chrome', 'opera']:
            option_.add_experimental_option('prefs', prefs)
            option_.add_experimental_option("detach", True)
            option_.add_argument(f"--user-data-dir={profile}")
            if binary_location:
                option_.binary_location = binary_location
            driver = self.browser_driver(option_)
        # firefox, web_driver manager is not suitable for this option
        else:
            option_.profile = profile
            option_.log.level = 'error'
            option_.set_preference("browser.download.folderList", 2)
            option_.set_preference("browser.download.manager.showWhenStarting", False)
            option_.set_preference("browser.download.dir", location)
            option_.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/x-gzip")
            driver = self.browser_driver(option_)

        return driver


if __name__ == "__main__":
    # br = Browser('chrome').browser(r'D:')
    br = Browser('firefox').browser(r'D:')
    # driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
    # print(dir(Browser('firefox')))
    # print(Path.home())
    # print(br.__setattr__)
    # br.browser(r'D:\yande.re')
    # options = webdriver.FirefoxOptions()
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # options.add_experimental_option("useAutomationExtension", False)
    # service = ChromeService(executable_path=DRIVER_FIREFOX_PATH)
    # driver = webdriver.Firefox(service=service, options=options)

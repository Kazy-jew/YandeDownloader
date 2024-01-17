#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
import json
import inspect

from copy import deepcopy
from src.settings import CONFIG_PATH
from src.utils.iohandler import Handler as hd

def read_ini():
    """
    read static config in conf/site.ini
    :return: ConfigParser instant
    """
    conf = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    return conf

def read_json(parser):
    """
    read dynamic config in .src/conf.d/parse.json
    :param parser: json file name
    :return: config dict or None
    """
    file = f"{parser}.json"
    return hd.jconf_reader(file)

def configuration(parser):
    """
    read configuration from .ini or .json file
    :param parser:should be the section name of .ini or name of json file;
            namely, if want to read config from both .ini and .json files,
            section name in .ini should be the same of json file name
    :return: list of config
    """
    conf_list = list()
    static_conf = read_ini()
    static_conf.read(CONFIG_PATH)
    static_conf[parser]['static_conf'] = json.dumps({k: v for k, v in static_conf[parser].items()})
    static_conf[parser]['static'] = ','.join([k for k, v in static_conf[parser].items()])
    conf_list.append(static_conf[parser])
    dynamic_conf = read_json(parser)
    if dynamic_conf:
        dynamic_conf['dynamic_conf'] = deepcopy(dynamic_conf)
        dynamic_conf['dynamic'] = ','.join(dynamic_conf.keys())
        conf_list.append(dynamic_conf)
    return conf_list


def add_attr(prefix):
    """
    base decorator for reading configuration from config
    and dynamically adding attribution to a class
    :param prefix: name of config file or config section
    :return: class
    """

    def apply_defaults(cls):
        configs = configuration(prefix)
        for config in configs:
            for name, value in config.items():
                if name != 'DEFAULT':
                    setattr(cls, name, value)
        return cls()

    return apply_defaults


def attribution(arg=None):
    """
    general decorator for reading configuration from config
    and dynamically adding attribution to a class
    :param arg: if not provided will read from class init parameter, the parameter
                should have the same name of config file or config section
    :return: class
    """

    def add_attribution(func):
        if inspect.isclass(func):
            cls = func
            prefix = arg
        else:
            cls = arg
            prefix = func
        configs = configuration(prefix)
        for config in configs:
            for name, value in config.items():
                if name != 'DEFAULT':
                    setattr(cls, name, value)
        try:
            return cls(prefix)
        except TypeError:
            return cls

    return add_attribution


if __name__ == '__main__':
    @attribution('yande')
    class YandeBase:
        pass


    @attribution
    class Browser:
        def __init__(self, name):
            self.name = name

    yb = YandeBase()
    # print(yb.__dict__)
    print(yb.__dir__())
    print(yb.dynamic_conf)
    print(yb.static_conf)

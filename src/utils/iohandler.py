#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
file name:    iohandler.py
author:       Ayase
created at:   10/16/2022 3:03 AM
project:      YandeDownloader
"""
import json
from pathlib import Path
from src.settings import STATUS_CONFIG_DIR, CACHE_DIR, JSON_DATA, TEXT_DATA


class Handler:

    @staticmethod
    def jconf_reader(file_: str):
        """
        read json configuration in src/conf.d/
        :param file_: file full name
        :return: conf dict or None
        """
        path = STATUS_CONFIG_DIR / file_
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                conf = json.load(f)
            return conf
        return {}

    @staticmethod
    def jconf_writer(file_: str, data: dict, dir_: Path = STATUS_CONFIG_DIR):
        """
        write image detailed info to json file
        :param file_:
        :param data:
        :param dir_:
        :return: None
        """
        p = dir_ / f"{file_}.json"
        if not dir_.exists():
            dir_.mkdir(parents=True)
        with open(p, 'w', encoding='utf-8') as w:
            json.dump(data, w, indent=4, ensure_ascii=False)

    @staticmethod
    def text_writer(file_: str, data: list[str], dir_: Path = CACHE_DIR):
        """
        write date range & image id to file
        :param file_: file full name
        :param data:
        :param dir_: data directory
        :return: None
        """
        p = dir_ / file_
        if not dir_.exists():
            dir_.mkdir(parents=True, exist_ok=True)
        with open(p, 'w', encoding='utf-8') as f:
            for info in data:
                f.write(f'{info}\n')

    @staticmethod
    def text_reader(file_: str, dir_: Path = CACHE_DIR):
        """
        read date range
        :param file_:
        :param dir_:
        :return: list
        """
        p = dir_ / file_
        if p.exists():
            with open(p, 'r', encoding='utf-8') as r:
                data = r.read().splitlines()
            return data
        else:
            return []

    @staticmethod
    def file_checker(file_: Path | str, dir_: Path = CACHE_DIR):
        """
        check if target file exist
        :param file_:
        :param dir_:
        :return: bool
        """
        result = Path(dir_/file_).exists()
        return result

    @staticmethod
    def jdata_reader(site: str, file_: str, dir_: Path = JSON_DATA):
        """
        read image detail from json file
        :param site: used as directory
        :param file_: file name
        :param dir_:
        :return: ImgData.imgData
        """
        p = dir_ / site / file_
        if not p.exists():
            return {}
        else:
            with open(p, 'r', encoding='utf-8') as r:
                img_data = json.load(r)
            return img_data

    @staticmethod
    def jdata_writer(site: str, file_: str, data: dict[str], dir_: Path = JSON_DATA):
        """
        write image detailed info to json file
        :param site:
        :param file_:
        :param data:
        :param dir_:
        :return: None
        """
        d = dir_ / site
        p = d / file_
        if not p.parent.exists():
            p.parent.mkdir(parents=True)
        with open(p, 'w', encoding='utf-8') as w:
            json.dump(data, w, indent=4, ensure_ascii=False)

    @staticmethod
    def flusher(site: str, year: str | int, file_names: list[str], methods: str = 'normal'):
        """
        move txt data file from assets/.cache/ to assets/data/txt/
        :param site:
        :param year:
        :param file_names:
        :param methods: 'all' | 'normal'
        :return: None
        """
        dst = TEXT_DATA / site / f"{year}"
        if not dst.exists():
            dst.mkdir(parents=True)
        match methods:
            case 'normal':
                for f in file_names:
                    p = CACHE_DIR / f
                    if p.exists():
                        p.replace(dst / f)
                return
            case 'all':
                pass
            case _:
                pass


if __name__ == "__main__":
    print(list(CACHE_DIR.parents))

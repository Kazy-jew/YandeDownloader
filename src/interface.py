#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time
import json

from src.settings import ImageData
from src.utils.confparser import attribution
from src.utils.dategenerator import Calendar
from src.archiver import Archiver, mkdir
from src.utils.logger import my_logger
from src.utils.iohandler import Handler as hd
from src.crawler import Downloader
# import signal
# import readchar


@attribution('yande')
class Yande(Archiver):
    def __init__(self, ):
        super().__init__()
        self.date_list = []
        self.static_conf = json.loads(self.static_conf)
        if sys.platform == 'win32':
            self.dl_path = self.winpath
        else:
            self.dl_path = self.posixpath
        self.static_conf.update({'dl_path': self.dl_path})
        self.logger = my_logger(self.prefix)

    @staticmethod
    def welcome():
        print('         Welcome to Yande.re Downloader !     ')
        print('------------------------------------------------------')
        print('|****************************************************|')
        print('|*** 1.download(date)  2.download remaining(date) ***|')
        print('|*** 3.update(date)    4.update remaining(date)   ***|')
        print('|*** 5.download(tag)   6.check remaining(tag)     ***|')
        print('|*** 7.update(tag)     8.download by json file    ***|')
        print('|*** 9.set year        10.exit                    ***|')
        print('|****************************************************|')
        print('-----------------------------------------------------|')

    def run(self):
        self.welcome()
        self.logger.info(f"download path: {self.dl_path}\n"
                         f"year: {self.dynamic_conf.get('year')}\n"
                         f"dates: {self.dynamic_conf.get('begin_date').replace('-', '/')}"
                         f"-{self.dynamic_conf.get('end_date').replace('-', '/')}\n"
                         f"month interval: {self.month_interval}")
        while True:
            choice = input('select option: ')
            match choice:
                case '1':
                    self.batch_dl()
                case '2':
                    self.check_dl()
                case '3':
                    self.update_chk()
                case '4':
                    self.update_chk_dl()
                case '5':
                    self.tag_dl()
                case '6':
                    self.check_tag()
                case '7':
                    pass
                case '8':
                    self.json_download()
                case '9':
                    self.set_year()
                case 'q':
                    print('exit')
                    raise SystemExit(0)
                case _:
                    print('Invalid Input !')

    def batch_dl(self):
        cld = Calendar(self.year)
        self.date_list = cld.input_dates()
        grouped_dates = cld.grouper(interval=self.month_interval)
        for dates in grouped_dates:
            self.dynamic_conf.update({'begin_date': dates[0], 'end_date': dates[-1]})
            self.logger.info({**self.dynamic_conf, **self.static_conf})
            finished = self.check_json(f'{self.prefix} {self.year}-{self.dynamic_conf.get("begin_date")}'
                                       f'_{self.year}-{self.dynamic_conf.get("end_date")}.json')
            if finished:
                self.logger.info(f'{self.year} {self.dynamic_conf.get("begin_date")} '
                                 f'{self.dynamic_conf.get("end_date")} has already finished downloading, exit')
                return self.batch_dl()
            self.date_list = dates
            hd.jconf_writer(self.sitetag, self.dynamic_conf)
            self.init_json_path()
            origin_id = self.id_fetcher(dates)
            id_list = origin_id
            self.downloader_y(dates, origin_id, id_list, eigenvalue=1)
            self.info_checker(self.json_file)
            self.move_json()
            self.logger.info('done, resting for 1 minute...')
            time.sleep(60)

    # check unfinished
    def check_dl(self, eigenvalue=1):
        finished = self.check_json(f'{self.prefix} {self.year}-{self.dynamic_conf.get("begin_date")}'
                                   f'_{self.year}-{self.dynamic_conf.get("end_date")}.json')
        if finished:
            self.logger.info(f'{self.year} {self.dynamic_conf.get("begin_date")} '
                             f'{self.dynamic_conf.get("end_date")} has already finished downloading, exit')
            return
        dates = hd.text_reader(f'{self.prefix} dates.txt')
        if not dates:
            dates = Calendar(self.year).date_range_between(self.begin_date, self.end_date)
        self.date_list = dates
        self.init_json_path()
        # original_id: the whole id list of date range
        original_id, remain_id = self.check_image(dates, origin_id=True)
        if len(remain_id) <= 10:
            self.timeout += 100
        self.downloader_y(dates, original_id, remain_id, eigenvalue)
        self.info_checker(self.json_file)
        self.move(dates)
        self.move_json()

    def update_chk_dl(self):
        pass

    # check update
    def update_chk(self):
        eigenvalue = 2
        dates = self.input_dates()
        self.date_list = dates
        json_info = self.init_json_path()
        self.sln_multi_dates(dates)
        original_id = self.update(dates)
        update_id = self.get_id(dates)
        self.downloader_y(dates, original_id, update_id, eigenvalue)

        # check unfinished update
        eigenvalue = 2
        self.chk_dl(eigenvalue)

    # download by tag(s)
    # def tag_dl(self):
    #     self.dl_tag = input("please input the tag you want to download: ")
    #     json_info = self.init_json_path()
    #     if settings.read_data(self.json_folder, self.json_file):
    #         tag_list = [*ImgData.imgData]
    #     else:
    #         tag_list = self.sln_tags(self.dl_tag)
    #     self.downloader_tag(tag_list, json_info)

    # def check_tag(self):
    #     if not self.dl_tag:
    #         self.dl_tag = input("please input the tag you want to check: ")
    #     json_info = self.init_json_path()
    #     remain_list = self.check_tag_dl(self.dl_tag)
    #     if remain_list:
    #         self.downloader_tag(remain_list, json_info)

    def json_download(self):
        pass

    # download by date
    def downloader_y(self, dates, original_id, id_list, eigenvalue):
        """
        yande.re downloader
        fin用于处理源网站图库更新后(图片由于不合要求被moderator删除)新的图片列表和本地的图片列表不一致的情况
        while及count_num用于处理本地网络原因导致的图片下载失败/同时检查源网页图片是否已被删除
        fetch_info_only: fetch image info without save to disk
        :param dates:
        :param original_id: 初始id列表
        :param id_list: 当前列表(需要下载的列表)
        :param eigenvalue: eigenvalue的值(1 or 2)用来区别1:初次下载时/ 2: update时, 下载完成后文件夹的创建和文件的移动
        :return:
        """
        urls = self.split_url()
        if id_list:
            dl = Downloader(**urls, **self.static_conf, **self.dynamic_conf)
        else:
            return
        retry = 0
        fin = True
        while id_list:
            # check if always fail, which indicating a block or network error
            t0 = time.time()
            success = dl.sln_download(id_list, json_info=self.json_info, json_file=self.json_file,
                                      to_disk=True, js=self.use_js, max_wait_time=self.timeout)
            if not success:
                self.logger.info(f'download aborted with error... sleeping for {60 * retry + 60}s')
                time.sleep(60 * retry + 60)
            id_list = self.check_image(dates)
            retry += 1
            if id_list:
                t1 = time.time()
                if t1 - t0 < 60 * retry:
                    self.logger.info(f'there may be outside errors, need an an hour long nap... ')
                    time.sleep(60 * 60)
                print('Retry times left:', 10 - retry)
                self.timeout += 200
            # 退出，同时检查源网页图片是否已被删除
            if retry == 10:
                # id_list为未下载的图片id, fin = True时，代表源网页的图片已删除， 否则fin = 未下载的图片列表
                fin = dl.sln_remove_deleted(id_list)
                break
        # 源网页的图片已删除时，更新本地图片列表文件(单个日期的图片列表文件不做改动)
        if fin is True:
            print('All images downloaded successfully')
            if id_list:
                new_list = list(set(original_id) - set(id_list))
                self.rewrite(dates, new_list)
            if eigenvalue == 1:
                self.move(dates)
            else:
                self.move(dates, updates=True)
        # 下载失败时，检查 & 下载或直接归档
        else:
            print('Please check the info above')
            tsuzuku = input(
                "Do you want to proceed archiving with broken downloads? s to proceed any else to quit: ")
            if tsuzuku == 's':
                if eigenvalue == 1:
                    self.move(dates)
                else:
                    self.move(dates, updates=True)
            else:
                return

    def id_fetcher(self, dates):
        urls = self.split_url()
        dl = Downloader(**urls, **self.static_conf, **self.dynamic_conf)
        id_list = dl.sln_multi_dates(dates)
        return id_list

    def info_checker(self, file_name=None):
        self.logger.info('check integrity of json info file...')
        if not file_name:
            file_name = input('please input the json file path under json/${site}: ')
        ImageData.imgData = hd.jdata_reader(self.prefix, file_name)
        id_list = [k for k, v in ImageData.imgData.items() if len(v) <= 3]
        if not id_list:
            self.logger.info(f'info of {file_name} is intact')
            return
        self.logger.info(f'{len(id_list)} images lack image info...{id_list}')
        urls = self.split_url()
        dl = Downloader(**urls, **self.static_conf, **self.dynamic_conf)
        dl.sln_download(id_list, json_info=self.json_info, json_file=file_name,
                        to_disk=False, js=self.use_js, max_wait_time=self.timeout)
        for pid in ImageData.imgData.keys():
            ImageData.imgData[pid]["download_state"] = True
        hd.jdata_writer(self.prefix, file_name, ImageData.imgData)

    # download by tag
    # def downloader_tag(self, tag_list, json_info):
    #     retry_num = 0
    #     going = []
    #     dl_tag_list = [x for x in tag_list if not ImgData.imgData[x].get('download_state')]
    #     print(f"{len(dl_tag_list)} in array...")
    #     while dl_tag_list:
    #         self.sln_download(dl_tag_list, max_wait_time=60, json_info=json_info, javascript=self.use_js)
    #         dl_tag_list = self.check_tag_dl(self.dl_tag)
    #         going = dl_tag_list
    #         retry_num += 1
    #         print('Retry times left: ', 4 - retry_num)
    #         if retry_num == 4:
    #             going = self.check_tag_dl(self.dl_tag)
    #             break
    #     if not going:
    #         print('All images downloaded successfully')
    #     else:
    #         print('check fail info')
    #         for x in going:
    #             print(f'{ImgData.imgData[x]["id"]}: {ImgData.imgData[x]["file_url"]}\n')


@attribution('konachan')
class Konachan(Archiver):

    def __init__(self):
        super().__init__()
        self.date_list = []
        self.static_conf = json.loads(self.static_conf)
        if sys.platform.startswith('win'):
            self.dl_path = self.winpath
        else:
            self.dl_path = self.posixpath
        self.static_conf.update({'dl_path': self.dl_path})
        self.logger = my_logger(self.prefix)

    @staticmethod
    def welcome():
        print('   Welcome to Konachan Downloader !   ')
        print('--------------------------------------')
        print('|************************************|')
        print('|*** 1.download      2.check   ******|')
        print('|*** 4.download(tag) 4.check(tag) ***|')
        print('|*** 5.set year      6.exit   *******|')
        print('|************************************|')
        print('¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯')

    def run(self):
        self.welcome()
        self.logger.info(f"download path: {self.dl_path}\n"
                         f"year: {self.dynamic_conf.get('year')}\n"
                         f"dates: {self.dynamic_conf.get('begin_date').replace('-', '/')}"
                         f"-{self.dynamic_conf.get('end_date').replace('-', '/')}\n")
        while True:
            choice = input('select operation: ')
            match choice:
                case '1':
                    self.batch_dl()
                case '2':
                    self.check_dl()
                case '3':
                    self.tag_dl()
                case '4':
                    self.check_tag()
                case '5':
                    self.set_year()
                case '6':
                    print('exit')
                    raise SystemExit(0)
                case _:
                    print('Invalid Input')

    def batch_dl(self):
        cld = Calendar(self.year)
        dates = cld.input_dates()
        self.date_list = dates
        self.dynamic_conf.update({'begin_date': dates[0], 'end_date': dates[-1]})
        self.logger.info({**self.dynamic_conf, **self.static_conf})
        hd.jconf_writer(self.sitetag, self.dynamic_conf)
        self.init_json_path()
        id_list = self.id_fetcher(dates)
        self.downloader_k(dates, id_list)
        self.info_checker(self.json_file)
        self.move(dates)
        self.move_json()

    def check_dl(self):
        dates = hd.text_reader(f'{self.prefix} dates.txt')
        if not dates:
            dates = Calendar(self.year).date_range_between(self.begin_date, self.end_date)
        self.date_list = dates
        self.init_json_path()
        id_list = self.check_image(dates)
        self.downloader_k(dates, id_list)
        self.info_checker(self.json_file)
        self.move(dates)
        self.move_json()

    def tag_dl(self):
        pass

    def check_tag(self):
        pass

    def id_fetcher(self, dates):
        urls = self.split_url()
        dl = Downloader(**urls, **self.static_conf, **self.dynamic_conf)
        id_list = dl.sln_multi_dates(dates)
        return id_list

    def downloader_k(self, dates, id_list):
        urls = self.split_url()
        if id_list:
            dl = Downloader(**urls, **self.static_conf, **self.dynamic_conf)
        else:
            return
        retry = 0
        while id_list:
            success = dl.sln_download(id_list, json_info=self.json_info, json_file=self.json_file,
                                      to_disk=True, js=self.use_js, max_wait_time=self.timeout)
            if not success:
                time.sleep(60*retry+60)
            id_list = self.check_image(dates)
            retry += 1
        self.move(dates)

    def info_checker(self, file_name=None):
        self.logger.info('check integrity of json info file...')
        if not file_name:
            file_name = input('please input the json file path under json/${site}: ')
        ImageData.imgData = hd.jdata_reader(self.prefix, file_name)
        id_list = [k for k, v in ImageData.imgData.items() if len(v) <= 3]
        if not id_list:
            self.logger.info(f'{file_name} is intact')
            return
        self.logger.info(f'{len(id_list)} images lack image info...{id_list}')
        urls = self.split_url()
        dl = Downloader(**urls, **self.static_conf, **self.dynamic_conf)
        dl.sln_download(id_list, json_info=self.json_info, json_file=file_name,
                        to_disk=False, js=self.use_js, max_wait_time=self.timeout)
        for pid in ImageData.imgData.keys():
            ImageData.imgData[pid]["download_state"] = True
        hd.jdata_writer(self.prefix, file_name, ImageData.imgData)

    def children_finder(self, stashed=True, by='date', file_name=None):
        self.logger.info('check if any parent lost their children...')
        if not file_name:
            file_name = input(f'please input the json file path under json/{self.prefix}: ')
        if stashed and by == 'date':
            file_path_name = f'by.DATE/{file_name}'
        elif stashed and by == 'tag':
            file_path_name = f'by.TAG/{file_name}'
        else:
            file_path_name = file_name
        ImageData.imgData = hd.jdata_reader(self.prefix, file_path_name)
        id_list = [k for k, v in ImageData.imgData.items()
                   if v['posts'][0]['has_children'] and len(v['posts'][0]['children']) == 0]
        if not id_list:
            self.logger.info(f'great! all parents got their children')
            return
        self.logger.info(f'{len(id_list)} parents {id_list[:10]}... lost their children...')
        urls = self.split_url()
        dl = Downloader(**urls, **self.static_conf, **self.dynamic_conf)
        dl.sln_download(id_list, json_info=self.json_info, json_file=file_path_name,
                        to_disk=False, js=self.use_js, broken=True, max_wait_time=self.timeout)
        hd.jdata_writer(self.prefix, file_path_name, ImageData.imgData)


@attribution('minitokyo')
class Minitokyo:
    def __init__(self):
        super().__init__()
        self.static_conf = json.loads(self.static_conf)
        if sys.platform == 'win32':
            self.dl_path = self.winpath
        else:
            self.dl_path = self.posixpath
        self.static_conf.update({'dl_path': self.dl_path})
        self.last_scan_id = self.dynamic_conf.get('last')
        self.logger = my_logger(self.prefix)
        print(self.static_conf)
        print(self.dynamic_conf)

    def run(self):
        self.logger.info(f"last scan id: {self.dynamic_conf.get('last')}\n")
        while True:
            choice = input('select operation: ')
            match choice:
                case '1':
                    self.last_scan_id += 1
                    self.scan_dl()
                case '2':
                    pass
                case '3':
                    pass
                case '6':
                    print('exit')
                    raise SystemExit(0)
                case _:
                    print('Invalid Input')

    def scan_dl(self):
        json_folder = self.static_conf.get('sitetag')
        mkdir(json_folder)
        end_id = int(input('please input the end id: '))
        if end_id <= self.last_scan_id:
            print(f'end id({end_id}) should be larger than last id({self.last_scan_id})')
            return self.scan_dl()
        dl = Downloader(**self.static_conf, **self.dynamic_conf)
        print(f'download from {self.last_scan_id} to {end_id}')

        new_last_id = dl.sln_minitokyo(self.last_scan_id, end_id)

        self.dynamic_conf.update({'last': new_last_id})
        self.last_scan_id = new_last_id

        hd.jconf_writer(self.sitetag, self.dynamic_conf)
        hd.jdata_writer(self.prefix, f'{self.prefix} {self.last_scan_id}-{new_last_id}.json', ImageData.imgData)




if __name__ == "__main__":
    # from src.settings import JSON_DATA
    # yr = Yande()
    # yr.run()
    # print(dir(yr))
    kc = Konachan()
    kc.run()

    # 767051
    # mini = Minitokyo()
    # mini.run()

    '''
    file_path = JSON_DATA / 'konachan.com/by.DATE'
    file_names = [x.name for x in file_path.iterdir()]
    print(file_names)
    for f in file_names:
        kc.children_finder(file_name=f)
    requests.get('https://konachan.com/post?page=1&tags=date%3A2021-12-01')
    def handler(signum, frame):
        msg = "Ctrl-c was pressed. Do you really want to exit? y/n "
        print(msg, end="", flush=True)
        res = readchar.readchar()
        if res == 'y':
            print("")
            exit(1)
        else:
            print("", end="\r", flush=True)
            print(" " * len(msg), end="", flush=True)  # clear the printed line
            print("    ", end="\r", flush=True)


    signal.signal(signal.SIGINT, handler)
    '''

    '''
    import numpy as np
    import sys

    def binary_matrix(n):
        length = 2**n
        matrix = np.zeros((length, n), dtype='int8')
        for i in range(n):
            matrix[:, i] = np.tile(np.repeat([0, 1], 2**(n-i-1)), 2**i)
        return matrix

    t0 = time.time()
    prod = binary_matrix(20)
    print(sys.getsizeof(prod) / 2**20, 'MiB')
    # print(prod)
    t1 = time.time()
    print(f'{t1-t0} s', f'{94.32326483726501/2**10}s')
    '''

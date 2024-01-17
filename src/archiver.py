#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
retrieving & updating & merging the id list, archive id list after download finished
"""
import re
import os
import json
import shutil
from src.settings import ROOT_DIR, JSON_DATA, TEXT_DATA, ImageData, CACHE_DIR, UPDATE_DIR
from pathlib import Path
from src.utils.dategenerator import Calendar
from src.utils.iohandler import Handler as hd


class Archiver:
    """
    @DynamicAttrs
    An image file and download state manager
    this class should always be used as a base class with classes in interface.py 
    """

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def split_url(self):
        urls = self.static_conf['urls'].split(',')
        url_dict = {
            'post_link': urls[1],
            'date_link': urls[0],
            'tag_link': urls[2]
        }
        return url_dict

    def check_json(self, file, by='by.DATE'):
        p = JSON_DATA
        return hd.file_checker(file, dir_= p / self.prefix / by)


    def init_from_json(self):
        p = JSON_DATA
        for i, _dir in enumerate(p.iterdir()):
            self.logger.info(f'{i}: {_dir}')
        p1 = p / f'{self.prefix}'
        files = [x for x in p1.iterdir() if x.is_file() and x.suffix == '.json']
        for i, _file in enumerate(files):
            print(f'{i}: {_file.name}')
        choice = input('please choose the file index to init: ')
        file = files[int(choice)]
        name = str(file.name)
        date_str = name.split('.json')[0].replace(f'{self.prefix} ', '')
        self.year = int(date_str.split('.')[0])
        date_in = date_str.split('.')[1].split('_')[0].split('-') + date_str.split('.')[1].split('_')[-1].split('-')
        self.date_list = Calendar(self.year).date_range_list(date_in)
        img_data = hd.jdata_reader(self.prefix, file)
        id_list = list(img_data.keys())
        id_list_file = CACHE_DIR / f'{self.prefix}.{self.year}-{self.date_list[0]}' \
                                                      f'_{self.year}-{self.date_list[-1]}.txt'
        hd.text_writer(id_list_file, id_list)
        self.logger.info('init from json done')
        return id_list

    # init json data download path
    def init_json_path(self):
        if self.date_list and self.tags:
            choice = input("please choose date (1) or tag (2) to set: ")
            if choice == "1":
                self.json_file = f'{self.prefix} {self.year}-{self.date_list[0]}_{self.year}-{self.date_list[-1]}.json'
            else:
                self.json_file = f'{self.prefix} tag#{self.tags}.json'
            return True
        elif self.date_list:
            self.json_file = f'{self.prefix} {self.year}-{self.date_list[0]}_{self.year}-{self.date_list[-1]}.json'
            return True
        elif self.tags:
            self.json_file = f'{self.prefix} tag#{self.tags}.json'
            return True
        else:
            return False

    def load_from_json(self):
        ImageData.imgData = hd.jdata_reader(self.prefix, self.json_file)
        id_list = list(ImageData.imgData.keys())
        dates_file = f'{self.prefix} {self.year}.{self.date_list[0]}_{self.year}.{self.date_list[-1]}.txt'
        hd.text_writer(dates_file, id_list)
        dates_dict = {k: f"{v['date'][0]}-{v['date'][1]:02d}-{v['date'][2]:02d}" for k, v in ImageData.imgData.items()}
        res = {}
        for i, v in dates_dict.items():
            res[v] = [i] if v not in res.keys() else res[v] + [i]
        for k, v in res.items():
            date_file = f'{self.prefix} {k}.txt'
            hd.text_writer(date_file, v)
        return id_list

    def get_dl_date(self):
        # read from .cache first, else read from json file
        file = f'{self.prefix} dates.txt'
        dates = hd.text_reader(file)
        if dates:
            self.date_list = [x.replace(f'{self.year}-', '') for x in dates if str(self.year) in x]
        else:
            self.init_from_json()
        return self.date_list

    # get_id是为了在继续下载时覆盖dates_list里原有的初始id列表，如在磁盘空间有限时，退出程序重新选择一小部分日期下载
    def get_id(self, dates):
        id_list = []
        if dates:
            # 更新下载日期范围
            site_dates = f'{self.prefix} dates.txt'
            hd.text_writer(site_dates, self.date_list)
            date_file = f'{self.prefix} {self.year}-{dates[0]}_{self.year}-{dates[-1]}.txt'
            # read from archived file directory if not exists in .cache directory
            id_list = hd.text_reader(date_file)
            if id_list:
                return id_list
            else:
                id_list = self.raw_id(dates)
        return id_list

    # raw_id为直接从原始id列表合并的初始列表
    def raw_id(self, dates):
        id_list = []
        p0 = TEXT_DATA / f'{self.prefix}'/ f'{self.year}'
        for _ in dates:
            file = f'{self.prefix} {self.year}-{_}.txt'
            date_id = hd.text_reader(file)
            if not date_id:
                date_id = hd.text_reader(file, p0)
                if not date_id:
                    raise ValueError(f"{file} does not exist!")
            id_list += date_id
        return id_list

    # 未下载的id列表
    def remain_id(self):
        file = f'{self.prefix} remains.txt'
        failed_id = hd.text_reader(file)
        return failed_id

    def update_id(self, dates):
        update_list = []
        for _ in dates:
            file = f'{self.prefix} {self.year}-{_}.update.txt'
            update_list += hd.text_reader(file, UPDATE_DIR / self.prefix)
        return update_list

    def rewrite(self, dates, new_list):
        # 更新初始列表文件，将源已删除的图片id去除
        file = f'{self.prefix} {self.year}-{dates[0]}_{self.year}-{dates[-1]}'
        hd.text_writer(file, new_list)
        self.logger.info('List updated')
        return

    # list3：初始id列表，list2: 已下载的id列表，list1: 下载的文件；返回初始列表, for yande.re
    def check_image(self, dates, origin_id=False):
        # print(self.prefix)
        self.logger.info('start checking downloads...')
        on_disk = Path(self.dl_path).iterdir()
        id_on_disk = list()
        if not self.json_file:
            self.init_json_path()
        self.logger.info('search for json file...')
        print(self.json_file)
        ImageData.imgData = hd.jdata_reader(self.prefix, self.json_file)
        if not ImageData.imgData:
            raise ValueError("No json Data file")
        for file in on_disk:
            name = file.name
            if name.lower().startswith(self.prefix) and (not name.endswith('crdownload')) and file.is_file():
                match self.prefix:
                    case 'yande.re':
                        id_on_disk.append(name.split(' ')[1])
                    case 'konachan.com':
                        id_on_disk.append(name.split(' ')[2])
                    case 'minitokyo.net':
                        pass
                    case _:
                        raise ValueError(f'{self.prefix}: not a supported prefix')
        for _ in id_on_disk:
            if ImageData.imgData.get(_):
                ImageData.imgData[_]["download_state"] = True
        # combine from text data directory if not exists in .cache directory
        _file_name_ = f'{self.prefix} {self.year}-{dates[0]}_{self.year}-{dates[-1]}'
        text_file = f'{_file_name_}.txt'
        json_date_file = f'{_file_name_}.json'
        full_id = hd.text_reader(text_file)
        if not full_id:
            full_id = self.raw_id(dates)
        diff = list(set(full_id) - set(id_on_disk))
        if len(diff) > 0:
            if len(diff) <= 10:
                self.logger.info(f'remain to be downloaded, [{", ".join(diff)}]')
            else:
                self.logger.info(f'{len(diff)} items remain')
        else:
            self.logger.info('No images to download')
        hd.jdata_writer(self.prefix, json_date_file, ImageData.imgData)
        remain_file = f'{self.prefix} remains.txt'
        hd.text_writer(remain_file, diff)
        if origin_id is True:
            return full_id, diff
        return diff

    def check_tag_dl(self, tag):
        list_all = Path(self.dl_path).iterdir()
        list_dl = []
        if not self.json_file:
            self.init_json_path()
        ImageData.imgData = hd.jdata_reader(self.prefix, self.json_file)
        for file in list_all:
            name = file.name
            if name.lower().startswith(self.prefix) and (not name.endswith('crdownload')) and file.is_file():
                match self.prefix:
                    case 'yande.re':
                        list_dl.append(name.split(' ')[1])
                    case 'konachan.com':
                        list_dl.append(name.split(' ')[2])
                    case 'minitokyo.net':
                        pass
                    case _:
                        raise ValueError(f'{self.prefix}: not a supported prefix')
        for _ in list_dl:
            ImageData.imgData[_]["download_state"] = True
        list_tag = [*ImageData.imgData]
        failed_dl = list(set(list_tag) - set(list_dl))
        # print(len(list_tag), len(list_dl), failed_dl)
        if len(failed_dl) > 0:
            if len(failed_dl) <= 10:
                self.logger.info(f'remain to be downloaded: {", ".join(failed_dl)}')
            else:
                self.logger.info(f'{len(failed_dl)} items remain')
            hd.jdata_writer(self.prefix, self.json_file, ImageData.imgData)
            return failed_dl
        else:
            self.logger.info('No images remain to download')
            return None

    def update(self, dates):
        dates_list = []
        p_ = TEXT_DATA / self.prefix / f'{self.year}'
        p_up = UPDATE_DIR / self.prefix
        if not p_.exists():
            p_.mkdir(parents=True)
        if not p_up.exists():
            p_up.mkdir(parents=True)
        for i in dates:
            file_name = f'{self.prefix} {self.year}-{i}'
            try:
                li1 = hd.text_reader(f'{file_name}.txt')
                li2 = hd.text_reader(f'{file_name}.txt', p_)
            except FileNotFoundError as e:
                return f'Specific File not Found: {e}'
            updated_img = list(set(li1) - set(li2))
            dates_list += updated_img
            if updated_img:
                hd.text_writer(f'{file_name}.update.txt', updated_img, p_up)
            else:
                self.logger.info('date {} no image updated'.format(i))
        hd.text_writer(f'{self.prefix} {self.year}-{dates[0]}_{self.year}-{dates[-1]}.txt', dates_list)
        return dates_list

    # archive image file by month
    def month_mv(self, dates, updates=None):
        list1 = Path(self.dl_path).iterdir()
        list2 = []
        for file in list1:
            i = file.name
            if i.lower().startswith(self.prefix) and (not i.endswith('crdownload')) and file.is_file():
                list2.append(i)
        month = dates[0].split('-')[0]
        if not updates:
            folder = f"{self.prefix} {self.year}.{month}"
            if not os.path.exists(os.path.join(self.dl_path, folder)):
                os.makedirs(os.path.join(self.dl_path, folder))
            for _ in list2:
                shutil.move(os.path.join(self.dl_path, _),
                            os.path.join(self.dl_path, folder))

    # move image file only, not id list file
    def move(self, dates, updates=None):
        list1 = Path(self.dl_path).iterdir()
        list2 = []
        for file in list1:
            i = file.name
            if i.lower().startswith(self.prefix) and (not i.endswith('crdownload')) and\
                    ('(1)' not in i) and file.is_file():
                list2.append(i)
        if len(list2) == 0:
            self.logger.info('No file to archive')
            return
        if not updates:
            for m in dates:
                d = TEXT_DATA / f'{self.prefix}' / f'{self.year}'
                f = f'{self.prefix} {self.year}-{m}.txt'
                p = d / f
                if not p.exists():
                    continue
                pair = hd.text_reader(f, d)
                folder = Path(self.dl_path) / f"{self.prefix} {self.year}.{m.replace('-', '.')}"
                if not folder.exists():
                    folder.mkdir(parents=True)
                for item in list2:
                    if self.prefix == 'konachan.com':
                        name_id = item.split(' ')[2]
                    elif self.prefix == 'yande.re':
                        name_id = item.split(' ')[1]
                    else:
                        name_id = item
                    if name_id in pair:
                        Path(f'{self.dl_path}/{item}').replace(folder / item)
        # for yande.re only
        else:
            folder = Path(self.dl_path) / \
                     f"{self.prefix} {self.year}.{dates[0].replace('-', '.')}-{self.year}.{dates[-1].replace('-', '.')}"
            if not folder.exists():
                folder.mkdir(parents=True)
            id_file = f'{self.prefix} {self.year}-{dates[0]}_{self.year}-{dates[-1]}'
            pair = hd.text_reader(id_file)
            for item in list2:
                name_id = item.split(' ')[1]
                if name_id in pair:
                    Path(f'{self.dl_path}/{item}').replace(folder / item)
        self.logger.info('archiving image...done')
        return

    def move_json(self):
        p = JSON_DATA / self.prefix / self.json_file
        dst = 'NULL'
        if self.date_list:
            dst = p.parent / 'by.DATE'
            if not dst.exists():
                dst.mkdir(parents=True)
            Path(p).replace(dst / self.json_file)
        elif self.tags:
            dst = p.parent / 'by.TAG'
            if not dst.exists():
                dst.mkdir(parents=True)
            Path(p).replace(dst / self.json_file)
        else:
            self.logger.info('not a specific download type, do nothing')
        self.logger.info(f'move {self.json_file} from {str(p.resolve())} to {str(dst.resolve())}')

    def set_year(self):
        year = input('please enter za year: ')
        self.year = int(year)
        self.dynamic_conf.update({'year': self.year})
        hd.jconf_writer(self.sitetag, self.dynamic_conf)
        self.logger.info(f'set year to {year}...')


def rmdir_current_dl():
    shutil.rmtree(Path().home() / '.cache')


def rename(var, directory=''):
    p = JSON_DATA / var / directory
    files = [x.name for x in p.iterdir() if x.is_file()]
    for file in files:
        naked = file.replace(f"{var} ", '').replace('.json', '')
        if '.' in naked:
            year = naked.split('.')[0]
            date1, date2 = naked.split('.')[1].split('_')
            new_name = f'{year}-{date1}_{year}-{date2}'
            print(naked)
            print(new_name)
            print(f"{file} -> {file.replace(naked, new_name)}")
            Path(p / file).replace(p / file.replace(naked, new_name))
            print("--------------")


def mkdir(path, root=JSON_DATA):
    return Path(root / path).mkdir(parents=True, exist_ok=True)



if __name__ == "__main__":
    # arr11 = list(CACHE_DIR.iterdir())
    # print(arr11[1].name)
    rename('konachan.com')

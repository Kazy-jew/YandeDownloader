#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
file name:    fileutil.py
author:       Ayase
created at:   10/24/2022 8:13 PM
project:      YandeDownloader
"""
import json
from pathlib import Path
from shutil import copy2, copy
from datetime import datetime, timedelta
from time import sleep

import pandas as pd
from tqdm import tqdm

from src.settings import JSON_DATA, TEXT_DATA
from src.utils.dategenerator import date_range_list
from src.utils.iohandler import Handler as Ha
# from src.utils.logger import my_logger


# logger = my_logger(Path(__file__).stem)


def monthly_agg(p: Path | str, d: Path | str = Path(r'D:\monthly'), prefix=None, year=None, month=None, mode='2'):
    """
    copy and archive image by a single month, the source folder name should be in form of 'prefix yyyy.mm.dd'
    :param p: source folder
    :param d: destine folder
    :param prefix:
    :param year:
    :param month:
    :param mode: use shutil.copy or shutil.copy2
    :return:
    """
    p = Path(p)
    dirs = [x for x in p.iterdir() if x.is_dir()]
    if prefix:
        dirs = [x for x in dirs if x.name.startswith(prefix)]
    name = dirs[0].name
    prefix, ymd = name.split(' ')
    year_, month_, date_ = ymd.split('.')
    if year:
        year_ = year
    if month:
        month_ = month
    dst_name = f'{prefix} {year_}.{month_:02}'
    file_list = list()
    for dir_ in dirs:
        if dir_.name.lower().startswith(dst_name.lower()):
            files = list(dir_.iterdir())
            file_list += files
    q = Path(d) / dst_name
    if not q.exists():
        q.mkdir(parents=True)
    print(f'{year_}-{month_} total files:', len(file_list))
    for f in (pbar := tqdm(file_list)):
        pbar.set_postfix({f'Copying to {q}': f'{f.name}'})
        if mode == '2':
            copy2(f, q)
        else:
            copy(f, q)


def archive_by_month(p, year, month1=None, month2=None, prefix=None, d=Path(r'D:\monthly'), mode='1'):
    """
    copy and archive image monthly across months
    :param p:
    :param d:
    :param year:
    :param month1:
    :param month2:
    :param prefix:
    :param mode:
    :return:
    """
    if month1 is None:
        month1 = 1
    if month2 is None:
        month2 = 12
    for m in range(month1, month2+1):
        monthly_agg(p, d, year=year, month=m, prefix=prefix, mode=mode)


def json_info_check():
    _year_ = '2008'
    num = 0
    year = int(_year_[:4])
    pre = "konachan.com"
    if '.' in _year_:
        n = f'{pre}/by.DATE/{pre} {year}-07-01_{year}-12-31.json'
        begin, end = '07-01', '12-31'
    else:
        n = f'{pre}/by.DATE/{pre} {year}-01-01_{year}-06-30.json'
        begin, end = '01-01', '06-30'
        if year == 2008 and pre == 'konachan.com':
            n = f'{pre}/by.DATE/{pre} {year}-01-13_{year}-06-30.json'
            begin, end = '01-13', '06-30'

    f = JSON_DATA / n
    with f.open('r', encoding='utf-8') as r:
        i = json.load(r)
    p = Path(fr'C:\Users\Ayase\Desktop\YandeDownloader\assets\data\txt\{pre}\{year}')
    txt = p.iterdir()
    period = date_range_list(year, begin, end)
    for _ in txt:
        if _.stem.split(' ')[1].replace(f'{year}-', '') in period:
            with _.open('r') as r_:
                l_ = r_.read().splitlines()
            num += len(l_)

    noinfo = [k for k, v in i.items() if len(v) != 8]
    lost = [k for k, v in i.items() if v["download_state"] is False]
    retr = [k for k, v in i.items() if v["retrieved"] is False]
    no_child = [k for k, v in i.items()
                if v['posts'][0]['has_children'] and len(v['posts'][0]['children']) == 0]
    print(f"total: {len(i)}\ntotal_txt: {num}\nnoinfo: {noinfo}\nno_children: {len(no_child)}\n"
          f"download_state_false: {len(lost)}\nretrieved_state_false: {len(retr)}\n")


def file_integrity(prefix='yande.re', file_folder=Path(r'D:\yande.re'), begin='2006-08', end='2010-01', remove=False, year_folder=True):
    """
    check the file id in json/txt/file_folder
    :param year_folder:
    :param end:
    :param begin:
    :param prefix:
    :param file_folder:
    :param remove:
    :return:
    """
    intact = True
    json_path = JSON_DATA / prefix / 'by.DATE'
    text_folder = TEXT_DATA / prefix
    t1 = pd.DataFrame({'date': pd.date_range(pd.to_datetime(f'{begin}-01'), pd.to_datetime(f'{end}-01'))})
    t2 = [d for d, g in t1.groupby(pd.Grouper(key='date', freq='MS'))]
    t2 = [x.strftime('%Y-%m-%d')[:-3] for x in t2]

    lost_children = []

    for m in tqdm(t2):  # (pbar := tqdm(t2)):
        # pbar.set_description(f'{m}', refresh=True)
        year = m.split('-')[0]
        json_file_filtered = [x for x in json_path.iterdir() if x.stem.lower().startswith(f'{prefix.lower()} {m}')]
        if not json_file_filtered:
            continue
        json_file = json_file_filtered[0]
        json_data = Ha.jdata_reader(prefix, json_file)
        no_info = [k for k, v in json_data.items() if len(v) != 8]
        children_info = [k for k, v in json_data.items() if v['posts'][0]['has_children'] and len(v['posts'][0]['children']) == 0]
        if len(children_info) > 0:
            lost_children.append({json_file.name: children_info})

        if no_info:
            print(f'{json_file.stem} lack image info: {", ".join(no_info)}')

        id_date = {k: v['post_date'] for k, v in json_data.items()}
        df = pd.DataFrame({'id': id_date.keys(), 'date': id_date.values()})
        date_id = {k: g['id'].tolist() for k, g in df.groupby('date')}
        for k, v in date_id.items():
            js_ids = v
            full_date = f'{year}-{k}'
            text_file = f'{prefix} {full_date}.txt'
            txt_ids = Ha.text_reader(text_file, text_folder/year)
            file_path = Path(file_folder / f'{prefix} {full_date.replace("-", ".")}')
            if year_folder:
                file_path = Path(file_folder / f"{year}" / f'{prefix} {full_date.replace("-", ".")}')
            file_ids = list(file_path.iterdir())
            # get the id from file name
            check_name = file_ids[0]
            id_checklist = [check_name.stem.split(' ')[1], check_name.stem.split(' ')[2]]
            id_position = [id_checklist.index(x)+1 for x in id_checklist if x.isdigit()][0]
            # print(f'id position: {id_position}')
            if not id_position:
                raise ValueError('cannot find a digital part')
            # remove duplicate
            if remove:
                [x.unlink(missing_ok=True) for x in file_ids if '(1)' in x.stem]
            file_ids = [x.stem.split(' ')[id_position] for x in file_ids]
            duplicate = [k for k, v in pd.Series(file_ids, dtype=str).value_counts().to_dict().items() if v > 1]
            not_in_js = [x for x in txt_ids if x not in js_ids]
            not_in_file = [x for x in txt_ids if x not in file_ids]
            if len(txt_ids) == len(js_ids) and len(js_ids) == len(file_ids) \
                    and not duplicate and not not_in_file and not not_in_js:
                # print(f'{full_date}: text, json, file {len(txt_ids)} ... equal')
                continue
            else:
                print(full_date, len(txt_ids), len(js_ids), len(file_ids), ' ', end='')
                intact = False
            if duplicate:
                print(f"duplicate: {duplicate}")
            if not_in_js:
                print(f"not in js: {not_in_js}")
            if not_in_file:
                print(f"not in file: {not_in_file}")
    if lost_children:
        print(f"lost children: {lost_children}")
    if intact is True:
        print('the image number in json, text and local file is consistent')


def children_integrity(prefix='yande.re'):
    json_path = JSON_DATA / prefix / 'by.DATE'
    json_files = Path(json_path).iterdir()
    for file in json_files:
        print(file.stem)
        with open(file, 'r', encoding='utf-8') as r:
            img_data = json.load(r)
        if len(img_data) == 0:
            print(f'no data!')

        no_info = [k for k, v in img_data.items() if len(v) != 8]
        children_info = [k for k, v in img_data.items() if v['posts'][0]['has_children'] and len(v['posts'][0]['children']) == 0]
        if len(children_info) > 0:
            print('lost children', children_info)

        if len(no_info) > 0:
            print('no info', no_info)


def update_json(prefix='yande.re', origin_file=None, patch_file=None):
    json_path = JSON_DATA / prefix / 'by.DATE'
    json_origin = json_path / origin_file
    json_patch = json_path / patch_file

    file1_bak = f"{origin_file}.bak"
    copy2(json_origin, json_path / file1_bak)

    with open(json_origin, 'r', encoding='utf-8') as r:
        origin_data = json.load(r)

    with open(json_patch, 'r', encoding='utf-8') as r:
        patch_data = json.load(r)

    print(len(origin_data))
    print(len(patch_data))
    patch = {k for k in patch_data if k not in origin_data}
    print(len(patch), patch)
    updated_data = {**origin_data, **patch_data}
    print(len(updated_data))

    with open(json_origin, 'w', encoding='utf-8') as w:
        json.dump(updated_data, w, indent=4, ensure_ascii=False)

    print('data updated')





if __name__ == "__main__":
    # for char in (bar := tqdm(["a", "b", "c", "d"])):
    #     bar.set_description(f"Processing {char}")
    #     sleep(0.7)
    # for char in (bar := tqdm(["a", "b", "c", "d"])):
    #     bar.set_postfix({'num_vowels': char})
    #     sleep(0.6)
    # archive_by_month(Path(r'D:\konachan.com'), 2021, 7)
    # file_integrity(prefix='Konachan.com', file_folder=Path(r'D:\konachan.com'), begin='2008-01', end='2021-12')
    file_integrity(prefix='yande.re', file_folder=Path(r'F:\yande.re'), begin='2022-01', end='2022-01', year_folder=False)
    # children_integrity()
    # update_json(patch_file='yande.re 2018-02-05_2018-02-05.json', origin_file='yande.re 2018-02-01_2018-02-28.json')

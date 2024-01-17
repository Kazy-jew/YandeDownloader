#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Downloader core, including fetching id list from web, downloading images & managing
the image list
1.download dates: use date_link
2.download tag : use tag_link
"""
import json
import re
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import pyautogui
from colorama import Fore, Style
from lxml import html
from tqdm import tqdm
from termcolor import colored
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException as TE
from selenium.common.exceptions import NoSuchElementException as NSEE
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options

from src.settings import ImageData
from src.utils.browser import Browser
from src.utils.iohandler import Handler as hd
from src.utils.logger import my_logger



class Downloader:

    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
            required kwargs:
                post_link   : link of image page
                browser     : browser name, Chrome preferred
                site        : image site name, i.e yande.re
                dl_path     : browser download directory
            required kwargs when download by date:
                year        : date time year
                date_link   : linkf of image date overview page
                date_list   : date range list
            other kwargs:
                timeout     : max time stay in a post page
                id_list     : image id list to be downloaded
        """
        self.illustrate = ''
        self.id_list = list()
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.logger = my_logger(self.prefix)

    def init_browser(self):
        p = Path(self.dl_path)
        if not p.exists():
            p.mkdir(parents=True)
        return Browser(self.browser).browser(self.dl_path)

    def sln_multi_dates(self, dates):
        """
        selenium realization of getting image id of multi dates, for ip restriction of anti-crawler
        :param dates: date range list
        :return: id list in date range
        """
        dates_list = list()    # id list of images in date range
        file_names = list()
        dates_dict = dict()    # {id: date} pair of images in date range
        date_file = f'{self.prefix} dates.txt'
        hd.text_writer(date_file, dates)
        driver = self.init_browser()
        for n in dates:
            # id list of a date
            date_list = list()
            # skip downloaded date
            file = f'{self.prefix} {self.year}-{n}.txt'
            exists = hd.file_checker(file)
            if exists:
                self.logger.info(f'list {self.year}-{n} already downloaded...')
                file_names.append(file)
                date_list += hd.text_reader(file)
                date_dict = {x: n for x in date_list}
                dates_dict.update(date_dict)
            else:
                url = self.date_link.format(1, self.year, n)
                driver.get(url)
                get_banned = self.konachan_cry(driver)
                while get_banned:
                    self.logger.info(f"{n} get banned...")
                    get_banned = self.konachan_cry(driver)
                try:
                    pages_num_element = driver.find_element(
                        By.XPATH, '//*[@id="paginator"]/div')
                    pages_num = int(pages_num_element.text.split(' ')[-3])
                    # print(f'Date {self.year}-{n} has {pages_num} pages, ', end='')
                except NSEE:
                    page_has_image = [driver.find_elements(By.XPATH, '//*[@id="post-list"]/div[3]/div[4]/p'),
                                      driver.find_elements(By.XPATH, '//*[@id="post-list"]/div[2]/div[4]/p')]
                    if any(page_has_image):
                        self.logger.info(f'Date {self.year}-{n} has no images')
                        continue
                    else:
                        pages_num = 1
                        # print(f'Date {self.year}-{n} has {pages_num} pages, ', end='')
                for i in range(1, pages_num + 1):
                    page_img = driver.find_elements(
                        By.XPATH, '//*[@id="post-list-posts"]/li')
                    no_image = False
                    while not page_img:
                        get_banned = self.konachan_cry(driver)
                        if get_banned:
                            page_img = driver.find_elements(
                                By.XPATH, '//*[@id="post-list-posts"]/li')
                        else:
                            chickens = driver.find_element(
                            By.XPATH, '//*[@id="post-list"]/div[3]/div[4]/p')
                            self.logger.info(chickens.text)
                            if 'chickens' in chickens.text:
                                self.logger.info(f'shitty! page {i} has no image yet it says have')
                                no_image = True
                                break
                    # some page in konachan image number is less than 21(usually 20)
                    if not no_image and self.prefix == 'konachan.com' and len(page_img) < 21:
                        self.logger.debug(f'page {i} has only {len(page_img)} images...')
                    date_list += [x.get_attribute('id') for x in page_img if not no_image]
                    if i < pages_num:
                        url = self.date_link.format(i+1, self.year, n)
                        driver.get(url)
                # print(f'{len(date_list)} images')
                self.logger.info(f'Date {self.year}-{n} has {pages_num} pages, {len(date_list)} images')
                date_list = [w.replace('p', '') for w in date_list]
                date_dict = {x: n for x in date_list}
                dates_dict.update(date_dict)
                if date_list:
                    file_names.append(file)
                    hd.text_writer(file, date_list)
                    self.logger.info('{}...done'.format(url.split('%3A')[-1]))
            dates_list += date_list
        image_txt = f'{self.prefix} {self.year}-{dates[0]}_{self.year}-{dates[-1]}.txt'
        hd.text_writer(image_txt, dates_list)
        self.id_list = dates_list
        image_json = re.sub(r'.txt$', '.json', image_txt)
        ImageData.imgData = hd.jdata_reader(self.prefix, image_json)
        if not ImageData.imgData:
            self.logger.info(f"{image_json} not exists...")
            self.logger.info('init ImageData file ...')
            ImageData.imgData = {x: {"retrieved": False,
                                     "download_state": False,
                                     "post_date": dates_dict[x]} for x in dates_list}
            hd.jdata_writer(self.prefix, image_json, ImageData.imgData)
        else:
            self.logger.info(f"ImageData file: {image_json} ... loaded")
        driver.close()
        self.logger.info(f'moving date file from CACHE_DIR to DATA_DIR...')
        hd.flusher(self.prefix, self.year, file_names)
        return self.id_list

    def sln_download(self, id_list, json_file=None, json_info=True, to_disk=True, js=True, broken=False, max_wait_time=60):
        """
        download core
        :param id_list: id to be donwloaded
        :param json_file : json_file_name
        :param json_info: write image info to json file
        :param to_disk: whether to save image to local disk, default True
        :param js: whether javascript is enabled, default True
        :param broken: sln_getInfo switch
        :param max_wait_time: max download wait time for a single page, effect only when js is enabled
        :return:
        """
        self.logger.info('start downloading...')
        count = 0
        self.logger.debug(f"json_info={json_info}, to_disk={to_disk}, javascript={js}, directory={self.dl_path}")
        driver = self.init_browser()
        for _ in tqdm(id_list):
            try:
                count += 1
                wait_time = max_wait_time
                url = self.post_link.format(_)
                driver.get(url)
                wait = WebDriverWait(driver, 2)
                # scroll the page
                # Get the height of the page using JavaScript
                # height = driver.execute_script('return document.body.scrollHeight')
                # Scroll down by 25% of the page height
                # scroll_amount = height * 0.20
                # driver.execute_script(f'window.scrollBy(0, {scroll_amount})')

                source = driver.page_source
                img_link = self.sln_getInfo(source, _, to_disk=to_disk, broken=broken)
                if not to_disk:
                    if count == 50:
                        self.logger.debug('count = 50, writing info to file...')
                        hd.jdata_writer(self.prefix, json_file, ImageData.imgData)
                        count = 0
                    continue
                if json_info:
                    if json_file is None:
                        e = 'json file name is needed when json_info set to True'
                        self.logger.critical(e)
                        raise SystemExit(-1)
                    if count == 50:
                        hd.jdata_writer(self.prefix, json_file, ImageData.imgData)
                        count = 0
                if not js and to_disk:
                    if not img_link:
                        e = 'image source link not exist'
                        self.logger.error(f"{_}: {e}")
                        raise ValueError(e)
                    driver.get(img_link)
                    pyautogui.hotkey('ctrl', 's')
                    time.sleep(1)
                    pyautogui.typewrite(['enter'])
                if js and to_disk:
                    while self.check_complete(driver) is False:
                        time.sleep(1)
                        wait_time -= 1
                        if wait_time <= 0:
                            speed = self.check_dl_speed(driver)
                            if speed > 20:
                                wait_time = max_wait_time
                            else:
                                self.logger.warning(f"post {_} max time {max_wait_time}s reached and download speed({speed}kib/s) is too low...")
                                break
                    info = self.check_complete(driver)
                    if info == 'deleted':
                        ImageData.imgData[_]['deleted'] = True
                        self.illustrate = info
                        self.logger.warning(f'image {_} has been removed from website.')
                # give browser time to save to disk
                if _ == id_list[-1] and js:
                    time.sleep(3)
            # time.sleep(2 + retry * 5)
            # if len(id_list) == 1:
            #     time.sleep(100)
            except TE:
                self.logger.error(f"{TE}.... at {_}")
                driver.execute_script("location.reload()")
            except Exception as e:
                self.logger.error(f'Unexpected Exception:\n{e}', exc_info=True)
                if json_info:
                    hd.jdata_writer(self.prefix, json_file, ImageData.imgData)
                driver.close()
                self.logger.error(f"{e}...download Interrupted at {_}")
                if 'CONNECTION' in f"{e}":
                    self.logger.warning('Connection Error...sleeping for 20 minutes')
                    time.sleep(1200)
                return False
        driver.close()
        hd.jdata_writer(self.prefix, json_file, ImageData.imgData)
        self.logger.info('...traverse list complete.')
        return True

    def sln_tags(self, tag, js=None):
        """
        get id list under a tag
        :param tag: tag to input
        :param js: if enabled, download with javascript script while crawling the pages, no need to call sln_download
        :return: id list of a tag
        """
        tag_list = []
        url = self.tag_link.format(1, tag)
        driver = self.init_browser()
        driver.get(url)
        try:
            pages_num_element = driver.find_element(
                By.XPATH, '//*[@id="paginator"]/div')
            pages_num = int(pages_num_element.text.split(' ')[-3])
            print(f'tag {tag} has {pages_num} pages, ', end='')
        except NSEE:
            page_has_image = driver.find_elements(
                By.XPATH, '//*[@id="post-list"]/div[3]/div[4]/p')
            if page_has_image:
                print(f'tag {tag} has no images')
                return list()
            else:
                pages_num = 1
                print(f"tag {tag} has {pages_num} pages, ", end='')
        for i in tqdm(range(1, pages_num + 1)):
            page_img = driver.find_elements(
                By.XPATH, '//*[@id="post-list-posts"]/li')
            while not page_img:
                self.konachan_cry(driver)
                page_img = driver.find_elements(
                    By.XPATH, '//*[@id="post-list-posts"]/li')
            tag_list += [x.get_attribute('id') for x in page_img]
            if i < pages_num:
                url = self.tag_link.format(i+1, tag)
                driver.get(url)
        tag_list = [x.replace('p', '') for x in tag_list]
        ImageData.imgData = {x: {
            "retrieved": False,
            "download_state": False} for x in tag_list}
        tag_file = self.prefix + " tag#" + tag
        hd.jdata_writer(self.prefix, tag_file, ImageData.imgData)
        driver.close()
        return tag_list

    @staticmethod
    def konachan_cry(driver, t=2):
        """
        check if get temporary banned, if so will sleep for a while
        :param t: sleeping time(s)
        :return: bool
        """
        cry = driver.find_elements(By.XPATH, '/html/body/div/p')
        if cry:
            time.sleep(t)
            driver.execute_script("location.reload()")
            return True
        return False

    @staticmethod
    def check_complete(driver):
        """
        check if download is finished
        need to enable javascript for this function
        :param driver: selenium driver
        :return: bool | str
        """
        case1 = driver.find_elements(By.XPATH, '//*[@id="tip2"]')
        if not case1: return False
        if case1[0].text:
            if 'COMPLETE' in case1[0].text.upper():
                return True
            elif 'DELETE' in case1[0].text.upper():
                return 'deleted'
            elif 'END' in case1[0].text.upper():
                return 'end'
            elif 'DOWNLOAD' in case1[0].text.upper():
                return False
        else:
            return False

    @staticmethod
    def check_dl_speed(driver):
        """
        check download speed
        :param driver:
        :return:
        """
        case1 = driver.find_elements(By.XPATH, '//*[@id="tipsProgress"]')
        if case1[0].text:
            if 'mib' in case1[0].text:
                return 1024
            elif 'kib' in case1[0].text:
                return float(case1[0].text.split('kib')[0])
        return 0

    def sln_getInfo(self, source, pid, to_disk=True, broken=False):
        """
        retrieved: whether been to the image page, init is False, set to True when has been to the image page.
        download_state: first set to True when fetching image page, set to False if not found in disk after check
        two conditions: 1. old json has info but no retrieved property -> go else branch (id, info)
                        2. new json has retrieved property but no info -> go if branch   (id, retrieve)
        retrieve: if json info fetched
        download_state: if saved to disk
        :param to_disk: bool to set download state
        :param broken: switch to control downloaded yet info is not intact
        :param source: driver.page_source
        :param pid: post id
        :return:
        """
        if not ImageData.imgData[pid]["retrieved"] or broken:
            id_data = {
                pid: {
                    "posts": [],
                    "pools": [],
                    "pool_posts": [],
                    "tags": None,
                    "date": [],
                    "post_date": ImageData.imgData[pid]["post_date"],
                    "download_state": to_disk,
                    "retrieved": True
                }
            }
            tree = html.fromstring(source)
            description = tree.xpath('//*[@id="post-view"]/div[1]/text()')[0].strip()
            self.illustrate = description
            if "delete" in description:
                id_data = {
                    pid: {
                        "post_date": ImageData.imgData[pid]["post_date"],
                        "deleted": True,
                        "description": re.sub(r'\n', '', description),
                        "download_state": broken
                    }
                }
            else:
                imgInfo = tree.xpath('//*[@id="post-view"]/script/text()')
                raw_string = imgInfo[0].strip()
                json_string = raw_string.lstrip(
                    'Post.register_resp(').rstrip(');')
                raw_data = json.loads(json_string)
                filter_list = ["id", "tags", "created_at", "updated_at", "score", "md5", "width",
                               "height", "file_size", "file_ext", "file_url", "rating", "has_children", "parent_id"]
                id_data[pid]["posts"] = [
                    {i: x[i] for i in x if i in filter_list} for x in raw_data["posts"]]
                c_timestamp = raw_data["posts"][0]["created_at"]
                fmt_date = datetime.fromtimestamp(c_timestamp)
                date_data = [fmt_date.year, fmt_date.month, fmt_date.day]
                id_data[pid]["date"] = date_data
                id_data[pid]["download_state"] = broken
                id_data[pid]["tags"] = raw_data["tags"]
                if raw_data["pools"]:
                    id_data[pid]["pools"] = [{i: x[i] for i in x if i not in [
                        "user_id", "is_public"]} for x in raw_data["pools"]]
                else:
                    id_data[pid]["pools"] = []
                if raw_data["pool_posts"]:
                    for _ in range(len(raw_data["pool_posts"])):
                        id_data[pid]["pool_posts"].append(
                            {i: raw_data["pool_posts"][_][i] for i in raw_data["pool_posts"][_] if i != 'active'})
                else:
                    id_data[pid]["pool_posts"] = []
                if raw_data["posts"][0]["has_children"]:
                    children_string = 'This post has'
                    children_node = tree.xpath(f"//*[contains(text(), '{children_string}')]")[0]
                    children_text = children_node.text_content()
                    children_post = re.findall(r'\d+', children_text)
                    children_post_id = [int(x) for x in children_post]
                    if len(children_post_id) == 0:
                        self.logger.warning(f"mama {pid} lost her children...")
                    id_data[pid]["posts"][0]["children"] = children_post_id
                    self.logger.debug(f"{pid} with children {children_post_id}")
            ImageData.imgData.update(id_data)
            source_img = raw_data["posts"][0].get("file_url", None)
            return source_img
        else:
            if ImageData.imgData[pid].get("deleted"):
                self.logger.warning(f"post {pid} deleted, skip")
            else:
                ImageData.imgData[pid]["download_state"] = False
                if not ImageData.imgData[pid].get("retrieved"):
                    ImageData.imgData[pid]["retrieved"] = True
            # downloaded, yet been deleted later, add deleted property
            if "delete" in self.illustrate:
                ImageData.imgData[pid]["deleted"] = True
        return

    def sln_remove_deleted(self, id_list):
        """
        selenium realization of remove_deleted, for ip restriction
        :param id_list: id need to check if been deleted by site or failed to download
        :return: True if id_list is empty else id_list
        todo: should use javascript return value to check, and image_info is not a good way, need to be replaced
        """
        id_to_remove = []
        print("checking the remaining posts...")
        driver = self.init_browser()
        for _ in tqdm(id_list):
            url = self.post_link.format(_)
            driver.get(url)
            WebDriverWait(driver, 3)
            source = driver.page_source
            tree = html.fromstring(source)
            deleted_info = tree.xpath('//*[@id="post-view"]/div[1]/text()')
            image_info = tree.xpath('//*[@id="image"]')
            if image_info:
                print(Fore.RED + 'Warning !\n',
                      Fore.BLUE + f'Image {colored(_, "green")} still exists \
                      but failed to be downloaded too many times, ',
                      Fore.BLUE + 'please check manually')
                print(Style.RESET_ALL)
            else:
                print(f'{_}:', deleted_info[0])
                # the post is deleted，remove from download list
                id_to_remove.append(_)
        driver.close()
        if len(id_list) == len(id_to_remove):
            # all the remaining post is deleted
            return True
        else:
            # return the failed to download image list
            return list(set(id_list) - set(id_to_remove))

    def sln_minitokyo(self, last_id, end_id=None):
        """
        minitokyo download core
        :param id_list: id to download
        :return:
        """
        driver = self.init_browser()
        # no need to login if use user profile:
        '''
        signal = 'confirm'
        circle_times = 0
        
        with open('./login', 'r') as r:
            userinfo = r.read().splitlines()
        account = userinfo[0]
        auth = userinfo[-1]
        # http_proxy = "127.0.0.1:7890"
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--proxy-server={}'.format(http_proxy))
        driver = webdriver.Chrome()  # options=chrome_options)
        url_login = 'http://my.minitokyo.net/login'
        driver.get(url_login)
        username = driver.find_element(By.XPATH, '//*[@id="username"]')
        username.send_keys(account)
        password = driver.find_element(By.XPATH, '//*[@id="content"]/form/li[2]/input')
        password.send_keys(auth)
        log_in = driver.find_element(By.XPATH, '//*[@id="content"]/form/li[3]/input')
        log_in.click()
        time.sleep(3)
        
        while signal == 'confirm':
            circle_times += 1
            list1 = os.listdir(self.dl_path)
            minitokyo_downloaded = []
            for name in list1:
                if name.endswith('jpg'):
                    minitokyo_image = name.split('.')[0]
                    minitokyo_downloaded.append(minitokyo_image)
            diff = list(set(id_list) - set(minitokyo_downloaded))
            if len(diff) == 0:
                signal = 'deny'
                print('Finally, all pictures have been downloaded')
            elif circle_times == 5:
                signal = 'deny'
                print('Almost downloaded with some exceptions')
                print(diff)
            else:
                print('start downloading...')
                for _ in tqdm(diff):
                    url = self.post_link.format(_)
                    driver.get(url)
                    location = driver.find_element(
                        By.XPATH, '//*[@id="image"]/p/a')
                    actions = ActionChains(driver)
                    actions.move_to_element_with_offset(
                        location, 100, 100).perform()
                    actions.context_click().perform()
                    pyautogui.typewrite(['down', 'down', 'enter'])
                    time.sleep(0.8)
                    pyautogui.typewrite(['enter'])
                print('download successful')
        '''
        print(dir(self))
        finale = False
        if end_id is None:
            end_id = 9e12
        while last_id < end_id and finale is False:
            url = self.urls.format(last_id)
            driver.get(url)
            self.logger.debug(url)

            # source = driver.page_source
            while self.check_complete(driver) is False:
                time.sleep(1)
            if self.check_complete(driver) == 'end':
                finale = True
                continue
            if self.check_complete(driver) == 'deleted':
                raw_info_data = {last_id: {'tags': {}, 'info': 'deleted'}}
                ImageData.imgData.update(raw_info_data)
                last_id += 1
                continue
            img_info = driver.find_element(By.ID, 'imageInfo')
            img_info_text = img_info.get_attribute("innerHTML")
            img_tag = driver.find_element(By.ID, 'imageTags')
            img_tag_text = img_tag.get_attribute("innerHTML")
            pattern = re.compile(r'-->|<!--')
            json_info = re.sub(pattern, '', img_info_text)
            json_tag = re.sub(pattern, '', img_tag_text)
            raw_info_data = {last_id: {'tags': json.loads(json_tag), 'info': json.loads(json_info)}}
            ImageData.imgData.update(raw_info_data)

            last_id += 1

        # print(json.dumps(ImageData.imgData, indent=2*' '))
        time.sleep(3)
        driver.close()
        return last_id


if __name__ == "__main__":
    params = {
        'post_link': 'https://konachan.com/post/show/{}',
        'date_link': 'https://konachan.com/post?page={}&tags=date%3A{}-{}',
        'browser': 'chrome',
        'prefix': 'konachan.com',
        'year': 2008,
        'dl_path': 'D:\konachan'
    }
    date_range = ['07-01', '07-02']
    dl = Downloader(**params)
    driver = dl.init_browser()
    # dl.sln_multi_dates(date_range)

    def get_image_child(source):
        tree = html.fromstring(source)
        string = 'This post has'
        node = tree.xpath(f"//*[contains(text(), '{string}')]")[0]
        text = node.text_content()
        children = re.findall(r'\d+', text)
        print(children)
        if len(children) > 0:
            print(children)
        else:
            print('wired')



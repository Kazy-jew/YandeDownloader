from lxml import html
from colorama import Fore, Style
from tqdm import tqdm
from termcolor import colored
import os
import re
import requests
import time
import urllib.parse
from src.archiver import Archive


class Downloader(Archive):
    """
    Below method is deprecated, not maintain any more
    """

    def __init__(self):
        super(Downloader, self).__init__()
        self.chrome_binary_switch = False
        self.illustrate = ''
        self.id_list = []

    def download(self, id_list):
        """
        deprecated, use sln download instead
        :param id_list:
        :return:
        """
        download_folder = self.site + ' ' + re.sub('-', '', self.date_link.split('%3A')[-1])  # 创建下载文件夹
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        print('start downloading...')
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 '
                                 'Firefox/67.0'}
        proxy_url = {'http': 'http://127.0.0.1:7890'}
        for i in tqdm(id_list):
            url = self.post_link.format(i)  # 图片页面的链接
            page = requests.get(url, headers=headers, proxies=proxy_url)
            tree = html.fromstring(page.content)
            if tree.xpath('//*[@id="png"]/@href'):  # 从图片页面获得原图片文件元素xpath
                # 图片页面没有png格式, 更换xpath
                source = tree.xpath('//*[@id="png"]/@href')
            else:
                source = tree.xpath('//*[@id="highres"]/@href')
            file_name = source[0].split('/')[-1]  # 从原图片地址的最后一段中获得图片描述的部分
            name = urllib.parse.unquote(file_name)  # 将其中的url转码为对应字符作为下载的文件名
            name_modify = re.sub('[*:?/|<>"]', '_', name)
            data = requests.get(source[0], headers=headers, proxies=proxy_url)
            with open(os.path.join(download_folder, name_modify), "wb") as file:  # 保存文件
                file.write(data.content)
            time.sleep(2)
        print('Download Successful')
        return

    # deprecated 生成原始id列表(多文件)和合并原始列表后的初始列表(单文件)，返回输入的日期
    def multi_dates(self, dates):
        """
        deprecated, use sln_multi_dates instead
        :param dates: date list
        :return: None
        """
        download_folder = '.cache'
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        # print(self.date_link)
        # id list of date range
        dates_list = []
        # id list of a date
        for n in dates:
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                              'Chrome/91.0.4472.164 Safari/537.36 OPR/77.0.4054.277'}
            proxy_url = {'http': '127.0.0.1:7890'}

            date_list = []
            # 已经下载完成的列表不重复下载
            if os.path.exists('./.cache/{}.{}-{}.txt'.format(self.site, self.year, n)):
                print('list {} already downloaded...'.format(n))
                with open('./.cache/{}.{}-{}.txt'.format(self.site, self.year, n), 'r') as r:
                    date_list += r.read().splitlines()
            else:
                # print('in else')
                mark_tag = None
                for i in range(1, 36):
                    if not self.date_link:
                        raise ValueError('no effect site link')
                    else:
                        url = self.date_link.format(i, self.year, n)
                    # print(url)
                    # In selenium, you can use driver.page_source to get the same result
                    # source = driver.page_source (here source equals page_.content)
                    # tree = html.fromstring(source)
                    page_ = requests.get(
                        url, headers=headers, proxies=proxy_url)
                    tree = html.fromstring(page_.content)
                    if self.site_tag == 'yande':
                        mark_tag = tree.xpath(
                            '//*[@id="post-list"]/div[2]/div[4]/p/text()')
                    elif self.site_tag == 'konachan':
                        mark_tag = tree.xpath(
                            '//*[@id="post-list"]/div[3]/div[4]/p/text()')
                    if not mark_tag:
                        date_list += tree.xpath(
                            '//*[@id="post-list-posts"]/li/@id')
                    elif mark_tag == ['Nobody here but us chickens!']:
                        date_list = [w.replace('p', '') for w in date_list]
                        break
                with open(os.path.join(download_folder, '{}.{}.txt'.format(self.site, url.split('%3A')[-1])), 'w') as f:
                    for item in date_list:
                        f.write('{}\n'.format(item))
                print('{}...done'.format(url.split('%3A')[-1]))
            dates_list += date_list
        with open(os.path.join(download_folder,
                               '{0}.{1}-{2}_{1}-{3}.txt'.format(self.site, self.year, dates[0], dates[-1])), 'w') as f:
            for item in dates_list:
                f.write('{}\n'.format(item))
        return

    # deprecated 确定图片未下载成功的原因：若源已经不存在则输出删除的信息，否则为本地原因
    def remove_deleted(self, id_list):
        """
        deprecated, use sln_remove_deleted instead
        :param id_list: passed id, vary each time
        :return: None
        """
        id_to_remove = []
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/73.0.3683.103 Safari/537.36'}
        proxy_url = {'http': 'http://127.0.0.1:7890'}
        for _ in tqdm(id_list):
            url = self.post_link.format(_)
            page = requests.get(url, headers=headers, proxies=proxy_url)
            tree = html.fromstring(page.content)
            deleted_info = tree.xpath('//*[@id="post-view"]/div[1]/text()')
            image_info = tree.xpath('//*[@id="image"]')
            if image_info:
                print(Fore.RED + 'Warning !\n',
                      Fore.BLUE + 'Image {} still exists \
                      but failed to be downloaded too many times, '.format(colored(_, 'green')),
                      Fore.BLUE + 'please check manually')
                print(Style.RESET_ALL)
            else:
                print('{}:'.format(_), deleted_info[0])
                # 原post已经删除，需要从列表中去除
                id_to_remove.append(_)
        if len(id_list) == len(id_to_remove):
            # 所有的图片网站上原post已经删除
            return True
        else:
            # 存在未下载成功的图片，返回该图片id列表
            return list(set(id_list) - set(id_to_remove))

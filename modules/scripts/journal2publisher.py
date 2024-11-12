import time

import requests
import re
import json

import tqdm
from habanero import Crossref
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from loguru import logger

from retrying import retry

STORAGE_PATH_BASE = 'W:\Personal_Project\grained_ai\projects\paper_doi_helper\storage'
DEFAULT_CHROMEDRIVER_PATH = 'W:\Personal_Project\grained_ai\projects\paper_doi_helper\src\chromedriver.exe'
DEFAULT_CHROMEDRIVER_VERSION = 129


class PaperCrawl:
    def __init__(self, if_headless=True, base_save_dir=None):

        if isinstance(base_save_dir, str):
            self.base_save_dir = Path(base_save_dir)
        elif isinstance(base_save_dir, Path):
            self.base_save_dir = base_save_dir
        else:
            self.base_save_dir = Path(STORAGE_PATH_BASE)

        logger.warning("Will create a default driver instance.")
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--lang=zh_CN.UTF-8")
        chrome_options.add_argument("--disable-dev-shm-usage")
        if if_headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # 禁用图片
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 禁用自动化控制特征
        # chrome_options.add_experimental_option('prefs', {'profile.managed_default_content_settings.javascript': 2})  # 禁用JavaScript
        chrome_options.add_argument('--incognito')  # 无痕模式
        chrome_options.page_load_strategy = 'eager'  # 设置页面加载策略

        self.driver = uc.Chrome(options=chrome_options,
                                driver_executable_path=DEFAULT_CHROMEDRIVER_PATH,
                                version_main=DEFAULT_CHROMEDRIVER_VERSION)
        self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {
                "userAgent": self.driver.execute_script(
                    "return navigator.userAgent"
                ).replace("Headless", "")
            },
        )

    def j2p(self, j_name):
        data = {
            'searchname': j_name,
            'searchissn': '',
            'searchfield': '',
            'searchimpactlow': '',
            'searchimpacthigh': '',
            'searchscitype': '',
            'view': 'search',
            'searchcategory1': '',
            'searchcategory2': '',
            'searchjcrkind': '',
            'searchopenaccess': '',
            'searchsort': 'relevance'
        }

        res = requests.post('https://www.letpub.com.cn/index.php?page=journalapp&view=search', data=data)
        ids = re.findall(
            rf"\?journalid=(\d+)&page=journalapp&view=detail\" target=\"_blank\">{j_name}",
            res.text)
        if not ids:
            return None

        id = ids[0]

        self.driver.get(f'https://www.letpub.com.cn/index.php?journalid=id&page=journalapp&view=detail')
        print("HERE")


def j2p(j_name: str):
    data = {
        'searchname': j_name,
        'searchissn': '',
        'searchfield': '',
        'searchimpactlow': '',
        'searchimpacthigh': '',
        'searchscitype': '',
        'view': 'search',
        'searchcategory1': '',
        'searchcategory2': '',
        'searchjcrkind': '',
        'searchopenaccess': '',
        'searchsort': 'relevance'
    }
    proxyAddr = "tun-vdpzuj.qg.net:11753"
    authKey = "7063131B"
    password = "C8FBFB115FD4"
    proxyUrl = "http://%(user)s:%(password)s@%(server)s" % {
        "user": authKey,
        "password": password,
        "server": proxyAddr,
    }
    print(proxyUrl)
    proxies = {
        "http": proxyUrl,
        "https": proxyUrl,
    }

    res = requests.post('https://www.letpub.com.cn/index.php?page=journalapp&view=search', data=data, proxies=proxies,verify=False,timeout = 20)
    ids = re.findall(
        rf"\?journalid=(\d+)&page=journalapp&view=detail\" target=\"_blank\">{j_name}",
        res.text)
    if not ids:
        logger.debug(res.text)
        if '您请求页面的速度过快' in res.text:
            raise Exception("您请求页面的速度过快")
        return None

    id = ids[0]

    res = requests.get(f'https://www.letpub.com.cn/index.php?journalid={id}&page=journalapp&view=detail', proxies=proxies,verify=False,timeout = 20)
    publisher = re.findall(
        rf"""出版商</td><TD  colspan="2" style="padding: 8px; border: 1px solid rgb\(221, 221, 221\); text-align: left; font-size: 12px; border-collapse: collapse;">(.*?)</td></tr><tr><TD style="padding: 8px; border: 1px solid rgb\(221, 221, 221\);""",
        res.text)
    if not publisher:
        logger.info(publisher)
        if '请求期刊信息系统页面数据过于频繁' in res.text:
            raise Exception("请求期刊信息系统页面数据过于频繁")
        logger.debug(res.text)
        return None
    return publisher[0]


if __name__ == "__main__":
    with open(r'W:\Personal_Project\grained_ai\projects\paper_doi_helper\src\all_journals.txt', 'r',
              encoding='utf-8') as f:
        text = f.read()
    out = {}
    todo = [i for i in text.split('\n') if i]
    for i in tqdm.tqdm(todo):
        time.sleep(5)
        if i in out:
            logger.success("Finished.")
        else:
            logger.info(i)
            p = None
            attempt = 0
            while 1:
                attempt += 1
                try:
                    logger.info(f"Attempt: {attempt}")
                    p = j2p(i)
                    break
                except Exception as e:
                    logger.error(str(e))
                    time.sleep(10 * attempt)
                    continue
            logger.success(p)
            out[i] = p
        with open('mapping.json', 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=2)



    # res = j2p('AMERICAN JOURNAL OF PHYSICAL ANTHROPOLOGY')
    # print(res)

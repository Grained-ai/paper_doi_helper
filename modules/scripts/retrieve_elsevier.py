import json

import tqdm
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from pathlib import Path
from loguru import logger

STORAGE_PATH_BASE = 'W:\Personal_Project\grained_ai\projects\paper_doi_helper\storage'
DEFAULT_CHROMEDRIVER_PATH = 'W:\Personal_Project\grained_ai\projects\paper_doi_helper\src\chromedriver.exe'
DEFAULT_CHROMEDRIVER_VERSION = 129


class PaperCrawl:
    def __init__(self, if_headless=False, base_save_dir=None):

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

    def get_journals_by_page(self, url):
        logger.info(f"Working on {url}")
        try:
            self.driver.get(url)
            # 等待页面加载完成，直到找到至少一个匹配的元素
            xpath = '//div[@datatest-id="search-result"]'
            wait = WebDriverWait(self.driver, 15)  # 等待最多10秒
            wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

            elements = self.driver.find_elements(By.XPATH, xpath)
            texts = [element.find_element(By.XPATH, './/span').text for element in elements]
            return texts
        except NoSuchElementException:
            logger.warning("未找到匹配的元素")
            return None
        except TimeoutException:
            logger.warning("超时：未能在指定时间内找到匹配的元素")
            return None
        except Exception as e:
            logger.warning(f"发生错误: {e}")
            return None

    def get_journals(self):
        output = {}
        if Path("output_elsevier.json").exists():
            with open("output_elsevier.json", 'r', encoding='utf-8') as f:
                output = json.load(f)
        for url in tqdm.tqdm(
                [f"https://www.elsevier.com/products/journals?query=&page={page}&sortBy=relevance" for page in
                 range(1, 313)]):
            if url in output:
                logger.success(f"Already finished.{url}")
                continue
            j_list = self.get_journals_by_page(url)
            output[url] = j_list
            if j_list is None:
                continue
            logger.success(f"Found {len(j_list)}")

        with open("output_elsevier.json", 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        return output


if __name__ == "__main__":
    ins = PaperCrawl()
    res = ins.get_journals()
    print(res)

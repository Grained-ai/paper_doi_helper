import json
from habanero import Crossref
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
from loguru import logger

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

    def get_abstract(self, doi):
        cr = Crossref()
        res = cr.works(ids=doi)
        logger.info(f"DOI: {doi} Details from <POST REQUEST>.")
        logger.success(json.dumps(res, indent=2, ensure_ascii=False))
        url = res['message']['link'][0]['URL'] if res['message']['link'] else None
        assert url, f'Failed to retrieve url for {doi}'
        logger.info(f"Starts to retrieve Abstract on page: <{url}>")

        try:
            self.driver.set_page_load_timeout(10)  # 设置为10秒
            self.driver.get(url)
        except Exception as e:
            logger.error(f"Failed to load page within timeout: {e}")
            return None

        # 使用显式等待等待元素出现
        wait = WebDriverWait(self.driver, 10)  # 最多等待10秒
        element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="Abs1-content"]')))

        return element.text

if __name__ == "__main__":
    ins = PaperCrawl(if_headless=False)
    res = ins.get_abstract('10.1038/427213b')
    logger.success(f"Abstract:\n{res}")
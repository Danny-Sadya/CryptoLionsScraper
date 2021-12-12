from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import os


class Scraper:

    def __init__(self):
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(executable_path=os.path.abspath(os.getcwd()) + "\chromedriver.exe", options=options)
        self.driver.set_page_load_timeout(30)

    def scrape_lions(self):
        try:
            self.load_website()
            time.sleep(10)
            self.scroll_page()


        except Exception as ex:
            print(ex)
        finally:
            self.driver.close()
            self.driver.quit()

    def load_website(self):
        self.driver.get("https://crypto.com/nft/collection/82421cf8e15df0edcaa200af752a344f?sort=salePrice&order=ASC")

    def scroll_page(self):
        try:
            SCROLL_PAUSE_TIME = 0.5

            last_height = self.driver.execute_script("return document.body.scrollHeight")
            # Get scroll height

            i = 0
            while True:
                # Scroll down to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(SCROLL_PAUSE_TIME)

                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    if i == 100:
                        break
                    else:
                        i += 1
                else:
                    i = 0
                last_height = new_height
        except Exception as ex:
            print('Error while scrolling: ', ex)


if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape_lions()

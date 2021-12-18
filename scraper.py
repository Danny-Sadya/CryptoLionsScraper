from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import re
import os


class Scraper:

    def __init__(self):
        self.properties = None
        self.lion_datas = []
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")
        self.driver = webdriver.Chrome(executable_path=os.path.abspath(os.getcwd()) + "\chromedriver.exe",
                                       options=options)
        self.driver.set_page_load_timeout(30)

    def scrape_lions(self):
        try:
            self.load_website()
            self.accept_cookies()
            self.properties = self.get_properties()
            print(f'Properties is: {self.properties}')
            # numbers_list = self.get_lions_txt()
            # for i in numbers_list:
            #     if int(i) > 7412:
            #         lion_url = self.find_leon(i)
            #         if lion_url is not None:
            #             lion_urls.append(lion_url)
            # self.scroll_page()
            lion_urls = self.get_lions_urls()
            for lion_url in lion_urls:
                self.get_lion_data(lion_url)

        except Exception as ex:
            print(ex)
        finally:
            with open('json_data.json', 'w+') as f:
                json.dump(self.lion_datas, f)
            self.driver.close()
            self.driver.quit()

    def get_lions_urls(self):
        with open('LionsUrls.txt', 'r') as f:
            urls = json.load(f)

        return urls

    # def get_lions_txt(self):
    #     with open('LionsFound1.txt', 'r') as f:
    #         lions = f.readlines()
    #     accept_numbers = []
    #     for lion in lions:
    #         if "not found" not in lion:
    #             accept_numbers.append(lion.split('#')[1].split(' ')[0])
    #
    #     return accept_numbers

    def get_properties(self):
        properties_box = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='css-5bzcow']"))
        )

        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        properties_box = soup.find('div', class_='css-5bzcow')
        properties = properties_box.find_all('div', class_='css-116v3dj')
        props = {'name': ''}

        for property in properties:
            property_name = property.find('div', class_='css-bzl3oz')
            propeperty_attributes = property.find_all('div', class_='css-1eygapw')
            for property_attribute in propeperty_attributes:
                property_attribute = property_attribute.find('div', class_='css-xlqv6d').text
                props[f'{property_attribute}'] = ''

        return props

    def accept_cookies(self):
        close_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//button[@class='onetrust-close-btn-handler onetrust-close-btn-ui banner-close-button onetrust-lg ot-close-icon']"))
            )
        time.sleep(1)
        close_button.click()

    def check_lion_number(self, i):
        try:
            lion_cards = WebDriverWait(self.driver, 3).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="css-seeu1x"]'))
            )
        except:
            print(f'Lion #{i} not found')
            return None

        for lion_card in lion_cards:
            lion_name = self.driver.find_element(By.XPATH, '//div[@class="NftCard_nftName__1Eh4U"]').text
            if lion_name == f"Loaded Lion #{i}":
                print(f'Lion #{i} found')
                return lion_card

        print(f'Lion #{i} not found')
        return None

    def find_leon(self, i):
        # search_query_button = self.driver.find_element(By.XPATH, "//input[@placeholder='Search collectibles']")
        search_query_button = WebDriverWait(self.driver, 300).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search collectibles']"))
        )

        search_query_button.click()
        search_query_button.clear()
        search_query_button.send_keys(f"Loaded Lion #{i}")
        search_query_button.send_keys(Keys.ENTER)
        lion = self.check_lion_number(i)
        if lion is None:
            return None

        lion_url = lion.find_element(By.XPATH, '//a[@class="no-style"]').get_attribute('href')

        return lion_url

    def get_lion_data(self, lion_url):
        try:
            self.driver.get(lion_url)
            data = self.properties.copy()
            lion_name = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='NftSummaryContainer_titleContainer__jO9V6']"))
            ).text
            data['name'] = lion_name

            properties_button = WebDriverWait(self.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="css-1y8qm99"]'))
            )

            soup = BeautifulSoup(self.driver.page_source, 'lxml')

            card_img_link = soup.find('img', class_='AssetImageContainer_artImage__2imcJ undefined css-84wpv7').get('src')
            # urllib.request.urlretrieve(card_img_link, f'images/{card_name}.jpg')
            properties_container = soup.find('div', class_="PropertiesContainer_properties__106RJ")
            properties_container = properties_container.find_all('div', class_=re.compile('PropertiesContainer_property_'))
            properties = []

            for property in properties_container:
                attribute = property.find('div', class_='PropertiesContainer_propertyTitle__1_mgb').text
                key = property.find('div', class_='PropertiesContainer_propertyBody__23p7y').text
                percentage = property.find('div', class_='PropertiesContainer_propertyPercentage__1olMU').text
                properties.append((
                {attribute: key},
                percentage))
                data[key] = percentage

            try:
                chain_details_button = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="ChainDetailsContainer_baseContainer__wwQGd"]'))
                )
                self.driver.execute_script("arguments[0].scrollIntoView(true);", chain_details_button)
                chain_details_button.click()
                time.sleep(0.5)
                window_before = self.driver.window_handles[0]
                window_after = self.driver.window_handles[1]
                self.driver.switch_to.window(window_after)
                chain_details_url = self.driver.current_url
                data['link'] = chain_details_url
                self.driver.close()
                self.driver.switch_to.window(window_before)
            except:
                data['link'] = ''
            # data = {'name': lion_name,
            #         'attributes': properties,
            #         'link': chain_details_url,
            #         }
            print("Data is: ", data)
            self.lion_datas.append(data)
        except Exception as ex:
            print(f'Exception in scraping leon: {ex}')

    def load_website(self):
        # self.driver.get("https://crypto.com/nft/collection/82421cf8e15df0edcaa200af752a344f?sort=salePrice&order=ASC")
        self.driver.get("https://crypto.com/nft/collection/82421cf8e15df0edcaa200af752a344f?sort=createdAt&order=DESC")

    def scroll_page(self):
        try:
            SCROLL_PAUSE_TIME = 1

            last_height = self.driver.execute_script("return document.body.scrollHeight")
            # Get scroll height
            i = 0
            while True:
                i += 1
                # Scroll down to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                # Wait to load page
                time.sleep(SCROLL_PAUSE_TIME)

                # Calculate new scroll height and compare with last scroll height
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    i += 1
                    if i == 100:
                        break
                else:
                    i = 0
                last_height = new_height
        except Exception as ex:
            print('Error while scrolling: ', ex)


if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape_lions()

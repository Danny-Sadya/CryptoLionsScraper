import json

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

import urllib.request
import re


def init_driver():
    options = ChromeOptions()
    ser = Service(os.path.abspath(os.getcwd()) + "\chromedriver.exe")
    options.add_argument("--start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(executable_path=os.path.abspath(os.getcwd()) + "\chromedriver.exe", options=options)
    driver.set_page_load_timeout(30)
    return driver


with open("lions_all.html", 'r', encoding='utf-8') as f:
    page = f.read()

soup = BeautifulSoup(page, 'lxml')
card_container = soup.find('div', id='root').find('div', class_='css-l7o0h').find('div', class_='css-1azrhzz')
card_list = card_container.find_all('div', class_='css-seeu1x')

cards = []

driver = init_driver()
try:
    i = 0
    for card in card_list:
        i += 1
        print(i)
        card_name = card.find('div', class_='NftCard_nftName__1Eh4U').text

        card_link = "https://crypto.com" + card.find('a', class_='no-style').get('href')
        driver.get(card_link)

        chain_details_button = WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="ChainDetailsContainer_baseContainer__wwQGd"]'))
        )

        properties_button = WebDriverWait(driver, 300).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="css-1y8qm99"]'))
        )

        soup = BeautifulSoup(driver.page_source, 'lxml')

        card_img_link = soup.find('img', class_='AssetImageContainer_artImage__2imcJ undefined css-84wpv7').get('src')
        urllib.request.urlretrieve(card_img_link, f'images/{card_name}.jpg')

        properties_container = soup.find('div', class_='css-181wa9l')
        properties_container = properties_container.find('div', class_=re.compile('PropertiesContainer_properties'))
        properties_container = properties_container.find_all('div', class_=re.compile('PropertiesContainer_property_'))
        properties = []

        for property in properties_container:
            attribute = property.find('div', class_='PropertiesContainer_propertyTitle__1_mgb').text
            key = property.find('div', class_='PropertiesContainer_propertyBody__23p7y').text
            percentage = property.find('div', class_='PropertiesContainer_propertyPercentage__1olMU').text
            properties.append({
                attribute: key,
                "percentage": percentage
            })

        chain_details_button.click()
        time.sleep(1)
        window_before = driver.window_handles[0]
        window_after = driver.window_handles[1]
        driver.switch_to.window(window_after)
        chain_details_url = driver.current_url
        driver.close()
        driver.switch_to.window(window_before)

        data = {'name': card_name,
                'attributes': properties,
                'link': chain_details_url,
                }
        print(data)
        cards.append(data)
        #
        # if i == 4:
        #     break

    # j = json.dumps(cards)
    # print('Exists data:')
    # print(j)
    with open('json_data.json', 'w+') as f:
        json.dump(cards, f)

except Exception as ex:
    print("Exception in run: ", ex)
    with open('json_data.json', 'w+') as f:
        json.dump(cards, f)

    input()

finally:

    driver.close()
    driver.quit()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

import os


# возвращает пустой драйвер
def create_driver(images_enabled=False):
    # оключение загрузки изображений для оптимизации
    chrome_options = Options()
    if not images_enabled:
        chrome_options.add_argument(f"--blink-settings=imagesEnabled=false")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    print('[DRIVER INFO] Driver created successfully.\n')
    # logs.log_info('[DRIVER INFO] Driver created successfully.')
    return driver


# закрывает все окна и завершает сеанс driver
def kill_driver(driver):
    driver.close()
    driver.quit()
    print('[DRIVER INFO] Driver was closed successfully.\n')
    # logs.log_info('[DRIVER INFO] Driver was closed successfully.')


# возвращает soup указанной страницы
def get_htmlsoup(driver):
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        return soup

    except Exception as _ex:
        print(f'[GET HTMLSOUP] An error occurred while trying to get soup - {_ex}.')
        # logs.log_warning(f'[GET HTMLSOUP] An error occurred while trying to get soup - {_ex}.')
        return None


def switch_url(driver, url):
    driver.execute_script('window.location.href = arguments[0];', url)

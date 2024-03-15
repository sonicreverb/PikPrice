import os.path

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from modules import BASE_DIR

# директория, предназначенная для сохраенения файлов из браузера
DOWNLOADS_PATH = os.path.join(BASE_DIR, 'modules', 'PriceUpdater', 'browser-downloads')


# возвращает драйвер с определёнными опциями
def create_driver(images_enabled=False, notifications_enabled=False):
    chrome_options = Options()
    prefs = {}
    # отключение загрузки изображений для оптимизации
    if not images_enabled:
        chrome_options.add_argument(f"--blink-settings=imagesEnabled=false")
    # отключение показа уведомлений браузера
    if not notifications_enabled:
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        prefs["profile.default_content_setting_values.notifications"] = 2

    # установка директории для скачивания файлов браузера
    prefs["download.default_directory"] = f"{DOWNLOADS_PATH}"

    # применение опций
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    print('[DRIVER INFO] Driver created successfully.')
    # logs.log_info('[DRIVER INFO] Driver created successfully.')
    return driver


# закрывает все окна и завершает сеанс driver
def kill_driver(driver):
    driver.close()
    driver.quit()
    print('[DRIVER INFO] Driver was closed successfully.')
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


# смена url текущего открытой вкладки драйвера
def switch_url(driver, url):
    driver.execute_script('window.location.href = arguments[0];', url)


def is_page_loaded(driver):
    return driver.execute_script('return document.readyState') == "complete"

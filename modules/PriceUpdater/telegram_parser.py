import os.path
import time
import pandas as pd
import json

from modules.TelegramAlerts import send_notification

from modules.PriceUpdater import driver_management as driver_manager
from modules.GoogleSheets import gsheets_management as gsheets_manager

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DEBUG = True

MODELS_TO_ARTICLES = {"Z15W002B1": "Ama136810161Sil", "Z15S002KY": "Ama136810161Spa",
                      "Z15Y002N3": "Ama136810161Sta", "Z1600040P": "Ama136810161Blu",
                      "Z15W002AW": "Ama13681016256Sil", "Z15S002KT": "Ama13681016256Spa",
                      "Z15Y002N1": "Ama13681016256Blu", "Z15W002B3": "Ama13681024256Sil",
                      "Z15S002L0": "Ama13681024256Spa", "Z15Y002N4": "Ama13681024256Sta",
                      "Z1600040R": "Ama13681024256Blu", "Z15W002B4": "Ama13681024512Sil",
                      "Z15S002L1": "Ama13681024512Spa", "Z15Y002N5": "Ama13681024512Sta",
                      "Z1600040S": "Ama13681024512Blu", "Z15W002AY": "Ama13681081Sil",
                      "Z15S002KV": "Ama13681081Spa", "Z15Y002N0": "Ama13681081Sta",
                      "Z1600040L": "Ama13681081Blu", "MLY03": "Ama1368108512Sil", "MLXX3": "Ama1368108512Spa",
                      "MLY23": "Ama1368108512Sta", "MLY43": "Ama1368108512Blu", "MLXY3": "Ama136888256Sil",
                      "MLXW3": "Ama136888256Spa", "MLY13": "Ama136888256Sta", "MLY33": "Ama136888256Blu",
                      "MGND3": "Ama1320878256Gol", "MGN93": "Ama1320878256Sil", "MGN63": "Ama1320878256Spa",
                      "MNEP3": "Amp1338108256", "MNEQ3": "Amp1338108512Sil", "MNEJ3": "Amp1338108512Spa",
                      "MYD82": "Amp1320888256Spa", "MYDC2": "Amp1320888512Sil", "MYD92": "Amp1320888512Spa",
                      "MKGT3": "Amp14p1016161Sil", "MKGQ3": "Amp14p1016161Spa", "MKGR3": "Amp14p81416512Sil",
                      "MKGP3": "Amp14p81416512Spa", "MK1H3": "Amp16m321Sil", "MK1A3": "Amp16m321Spa",
                      "MK1F3": "Amp16p1016161Sil", "MK193": "Amp16p1016161Spa", "MK1E3": "Amp16p101616512Sil",
                      "MK183": "Amp16p101616512Spa", "MQKP3": "Ama15M28256SSDSpa",
                      "MQKR3": "Ama15M28256SSDGra", "MQKU3": "Ama15M28256SSDSta", "MQKW3": "Ama15M28256SSDBlu",
                      "MQKV3": "Ama15M28512SSDSta", "MQKT3": "Ama15M28512SSDGra", "MQKX3": "Ama15M28512SSDBlu",
                      "MQKQ3": "Ama15M28512SSDSpa", "MV7N2": "AA2Whi", "MPNY3": "AA3Whi", "MME73": "AA3MWhi",
                      "MLWK3": "AAPMWhi"}


# получаем токены браузера с авторизованным телеграмм аккаунтом
def get_credentials(driver):
    tokens = driver.execute_script(
        "var tokens = {};\
        for (var i = 0; i < localStorage.length; i++){\
            tokens[localStorage.key(i)] = localStorage.getItem(localStorage.key(i));\
            };\
        return tokens;"
    )

    with open("telegram_tokens.json", "w") as f:
        json.dump(tokens, f)

    return tokens


# возвращает содержимое telegram_tokens.json
def load_credentials():
    if not os.path.exists("telegram_tokens.json"):
        return None

    with open("telegram_tokens.json", "r") as f:
        credentials = json.load(f)
    return credentials


# support функция для установки токенов в драйвер
def set_storage_item(driver, key, value):
    driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", key, value)


# установка токенов с авторизацией в телеграм для драйвера
def set_credentials(driver):
    credentials = load_credentials()
    if not credentials:
        return None

    for key, value in credentials.items():
        set_storage_item(driver, key, value)
    return True


# определяет цвет для артикула позиции
def define_article_color(product_name_lower: str):
    if "black" in product_name_lower:
        return "Bla"
    elif "white" in product_name_lower:
        return "Whi"
    elif "blue" in product_name_lower:
        return "Blu"
    elif "purple" in product_name_lower:
        return "Pur"
    elif "red" in product_name_lower:
        return "Red"
    elif "green" in product_name_lower:
        return "Gre"
    elif "pink" in product_name_lower:
        return "Pin"
    elif "starlight" in product_name_lower:
        return "Sta"
    elif "gold" in product_name_lower:
        return "Gol"
    elif "silver" in product_name_lower:
        return "Sil"
    elif "yellow" in product_name_lower:
        return "Yel"
    elif "natural titanium" in product_name_lower:
        return "Nat"

    return ""


# определяет объём памяти для артикула позиции
def define_article_memory(product_name_lower: str):
    if "64gb" in product_name_lower:
        return "64"
    elif "128gb" in product_name_lower:
        return "128"
    elif "256gb" in product_name_lower:
        return "256"
    elif "512gb" in product_name_lower:
        return '512'
    elif "1tb" in product_name_lower:
        return '1'
    elif "2tb" in product_name_lower:
        return '2'

    return ""


# определяет артикул pikprice по наименованию товара
def generate_article(product_name: str):
    article = None

    product_name_parts = product_name.split()
    product_name_lower = product_name.lower()

    try:
        # артикулы для айфонов
        if "iphone" in product_name_lower:
            article = "Ai"

            # модель
            model = product_name_parts[product_name_parts.index('iPhone') + 1]
            article += model

            if "pro max" in product_name_lower:
                article += "PM"
            elif "pro" in product_name_lower:
                article += 'P'
            elif "plus" in product_name_lower:
                article += "Pl"
            elif "mini" in product_name_lower:
                article += 'm'

            # память
            article += define_article_memory(product_name_lower)

            # цвет
            article += define_article_color(product_name_lower)

            if "2 sim" in product_name_lower:
                article += "D"

        # артикулы для часов
        elif "apple watch" in product_name_lower:  # todo
            article = "AW"
            if "se" in product_name_lower.split():
                article += "SE"
            elif "series 7" in product_name_lower:
                article += "S7"
            elif "series 8" in product_name_lower:
                article += "S8"
            elif "series 9" in product_name_lower:
                article += "S9"
            elif "ultra 2" in product_name_lower:
                article += "U2"
            elif "ultra" in product_name_lower:
                article += "U"

            if "40mm" in product_name_lower:
                article += "40"
            elif "41mm" in product_name_lower:
                article += "41"
            elif "44mm" in product_name_lower:
                article += "44"
            elif "45mm" in product_name_lower:
                article += "45"
            elif "49mm" in product_name_lower:
                article += "49"

            # цвет
            if "black" in product_name_lower:
                article += "Bla"
            elif "white" in product_name_lower:
                article += "Whi"
            elif "blue" in product_name_lower:
                article += "Blu"
            elif "purple" in product_name_lower:
                article += "Pur"
            elif "red" in product_name_lower:
                article += "Red"
            elif "green" in product_name_lower:
                article += "Gre"
            elif "pink" in product_name_lower:
                article += "Pin"
            elif "starlight" in product_name_lower:
                article += "Sta"
            elif "gold" in product_name_lower:
                article += "Gol"
            elif "silver" in product_name_lower:
                article += "Sil"
            elif "yellow" in product_name_lower:
                article += "Yel"
            elif "natural titanium" in product_name_lower:
                article += "Nat"
            elif "midnight" in product_name_lower:
                article += "Mid"
            elif "space gray" in product_name_lower:
                article += "Spa"

            if "cellular" in product_name_lower:
                article += "C"

        elif "apple ipad" in product_name_lower:
            article = "Ap"
            if "mini (2021)" in product_name_lower:
                article += "m21"
            elif "pro 11 (2021)" in product_name_lower:
                return None  # нет такой позиции в каталоге pikprice
            elif "2021" in product_name_lower:
                article += "10221"
            elif "pro 11 (2022)" in product_name_lower:
                article += "P1122"
            elif "pro 12.9 (2022)" in product_name_lower:
                article += "P12922"
            elif "air (2022)" in product_name_lower:
                article += "A22"
            elif "2022" in product_name_lower:
                article += "10922"

            article += define_article_memory(product_name_lower)

            if "wi-fi + cellular" in product_name_lower:
                article += "WC"
            elif "wi-fi" in product_name_lower:
                article += "W"

            article += define_article_color(product_name_lower)

        else:  # для макбуков и некоторых наушников возможность определения артикулов по моделям
            for model in MODELS_TO_ARTICLES:
                if model in product_name:
                    return MODELS_TO_ARTICLES.get(model)

    except Exception as _ex:
        print(f'[GENERATE ARTICLE] Во время определения артикула позиции \'{product_name}\' возникла ошибка: {_ex}.')
    if DEBUG:
        print(product_name, article)
    return article


# авторизация в телеграмме и получение файла с прайс-листом из канала
def download_last_tg_price():
    driver = driver_manager.create_driver(images_enabled=True, notifications_enabled=False)
    wait = WebDriverWait(driver, 30)

    driver.get("https://web.telegram.org")
    set_credentials(driver)
    driver.refresh()
    time.sleep(30)

    if not set_credentials(driver) or "Log in" in driver.page_source:
        input("[TELEGRAM PRICE PARSER] Пройдите авторизацию в Telegram, после чего нажмите ENTER.")
        send_notification("[PIKPRICE TG PRICE PARSER] Необходимо пройти авторизацию в Telegram!")
        get_credentials(driver)

    # открытие тг-канала, который будем парсить
    search_classname = 'form-control'
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, search_classname)))
    except TimeoutException:
        search_classname = 'input-field-input is-empty input-search-input'

    search_box = driver.find_element(By.CLASS_NAME, search_classname)
    search_box.send_keys("GreenApp24")
    time.sleep(2)
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)

    # клик по файлу последнего прайс-листа для его сохранения
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'file-icon-container')))
    last_price_elem = driver.find_elements(By.CLASS_NAME, 'file-icon-container')[-1]
    ActionChains(driver).move_to_element(last_price_elem).perform()
    ActionChains(driver).click(last_price_elem).perform()

    print('[TELEGRAM PRICE PARSER] Файл с прайс-листом успешно сохранён!')
    print('[TELEGRAM PRICE PARSER] Браузер автоматически закроется через 30 секунд.')
    time.sleep(30)
    driver.close()


# парсинг цен из загруженного прайс-листа и их обновление в каталоге пикпрайс
def upload_tg_prices():
    # получаем артикулы из таблицы pikprice
    pikprice_articles = gsheets_manager.read_column(gsheets_manager.PRODUCT_ARTICLES_COLUMN)[1:]
    upload_prices = [['цена не найдена']] * len(pikprice_articles)

    tg_price_dict = {}

    # получаем именования из самого свежего прайс-листа
    downloads_directory = driver_manager.DOWNLOADS_PATH
    files = os.listdir(downloads_directory)

    tg_price_path = None
    newest_mtime = 0

    for file in files:
        file_path = os.path.join(downloads_directory, file)
        if os.path.isfile(file_path):
            mtime = os.path.getmtime(file_path)
            if mtime > newest_mtime:
                tg_price_path = file_path
                newest_mtime = mtime

    tg_price_xls_data = pd.read_excel(tg_price_path)

    for value in tg_price_xls_data.values[6:]:
        tg_price_dict[str(value[0]).strip()] = value[-1]

    for product_name in tg_price_dict:
        product_generated_article = generate_article(product_name)
        try:
            product_position = pikprice_articles.index(product_generated_article)
            if upload_prices[product_position] == ['цена не найдена']:
                upload_prices[product_position] = [tg_price_dict[product_name]]
            else:
                avg_price = int((upload_prices[product_position][0] + tg_price_dict[product_name]) / 2 // 100 * 100)
                upload_prices[product_position] = [avg_price]
                # округление средней цены
        except ValueError:  # если .index() выдал ошибку, т. е. артикула нет в исходной PK таблице
            pass

    print(f"[TELEGRAM PRICE PARSER] Найдены цены для {len(upload_prices) - upload_prices.count(['цена не найдена'])}"
          f" позиций.")

    gsheets_manager.write_data(f"{gsheets_manager.TELEGRAM_PRICE_COLUMN}2:{gsheets_manager.TELEGRAM_PRICE_COLUMN}",
                               upload_prices)
    print('[TELEGRAM PRICE PARSER] Цены успешно загружены в таблицу!')


def start_telegram_parsing():
    download_last_tg_price()
    upload_tg_prices()

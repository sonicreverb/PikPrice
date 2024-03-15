import re
import time

import modules.PriceUpdater.driver_management as driver_manager
import modules.GoogleSheets.gsheets_management as gsheet_manager

from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver import Keys
from selenium.common.exceptions import NoSuchElementException


# функция для парсинга минимальной и средней цены позиции с наименованием good_name на мегамаркете
def parse_prices(good_name: str, _driver):
    # driver_manager.switch_url(_driver, "https://megamarket.ru/")
    search_field_input = _driver.find_element(By.CLASS_NAME, 'search-field-input')
    search_field_input.click()

    # очищаем поле ввода после закрытия
    try:
        clear_search_field_button = _driver.find_element(By.CLASS_NAME, "header-search-form__cancel-button")
        clear_search_field_button.click()
    except NoSuchElementException:
        pass

    # вводим наименование продукта и нажимаем enter
    search_field_input.send_keys(good_name)
    ActionChains(_driver).send_keys(Keys.ENTER).perform()

    time.sleep(2)

    soup = driver_manager.get_htmlsoup(_driver)
    prices_li = []

    item_money_blocks = soup.find_all('div', class_='item-money')
    if not item_money_blocks:
        raise Exception("не найдены позиции для парсинга")

    for item_money_block in item_money_blocks:
        price_block = item_money_block.find('div', class_='item-price')
        if price_block:
            price = price_block.get_text()
            price = int(re.sub(r"\D", "", price))
            prices_li.append(price)
        else:
            print(f'[SBERMEGAMARKET PARSER] WARNING! Не удалось получить цену для элемента {price_block}')

    # расчёт средней и минимальной цены
    medium_price = 0
    for price in prices_li:
        medium_price += price

    medium_price = int((medium_price / len(prices_li)) / 100) * 100
    minimum_price = int(min(prices_li) / 100) * 100

    return medium_price, minimum_price


# запускает процесс парсинга цен по сбермегамаркету для наименований из каталога в гугл таблице
def start_megamarket_parsing():
    driver = driver_manager.create_driver()
    driver.get("https://megamarket.ru/")

    # нажимаем кнопку, чтобы закрыть всплывающие окно, закрывающие доступ к сайту
    try:
        close_region_button = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div/div/div/div/div/div/div/button')
        close_region_button.click()
    except NoSuchElementException:
        pass

    # чтение наименований из гугл-таблицы (каталога)
    goods_names = gsheet_manager.read_column("A")[1:]  # со второй строки, т.к первая - название столбца
    upload_medium_prices = []
    upload_minimum_prices = []

    # было ли закрыто окно всплывающие окно с акциями?
    flag_annoying_pc_closed = False

    for good_name in goods_names:
        med_price = 'не найдена'
        min_price = 'не найдена '

        try:
            print(f"[SBERMEGAMARKET PARSER] Текущия позиция для парсинга: {good_name}")
            med_price, min_price = parse_prices(good_name, driver)
            print(f"[SBERMEGAMARKET PARSER] Успешно получены цены позиции: {good_name}. MIN: {min_price}р. "
                  f"MED: {med_price}р. ")
        except Exception as _ex:
            print(f"[SBERMEGAMARKET PARSER] Во время парсинга возникла ошибка: {_ex}")
        finally:
            upload_medium_prices.append([med_price])
            upload_minimum_prices.append([min_price])

            # так как всплывающие окно с акциями возникает после первого товара, то соответственно:
            if not flag_annoying_pc_closed:
                time.sleep(10)  # единоразовая задержка перед тем, как закрыть всплывающее окно
                # почему-то по-человечески не получается найти элемент кнопки (выдаёт null), поэтому такой обход
                js_click_script = "document.querySelector('a').click()"
                driver.execute_script(js_click_script)
                flag_annoying_pc_closed = True

        time.sleep(1)  # задержка между парсингом позиций

    driver_manager.kill_driver(driver)

    # запись полученных цен в гугл таблицу (каталог)
    gsheet_manager.write_data("R2:R", upload_medium_prices)
    gsheet_manager.write_data("S2:S", upload_minimum_prices)

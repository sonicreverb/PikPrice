import time
import modules.PriceUpdater.driver_management as driver_manager

from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver import Keys


# функция для парсинга минимальной и средней цены позиции с наименованием good_name на мегамаркете
def parse_prices(good_name: str, _driver):
    driver_manager.switch_url(_driver, "https://megamarket.ru/")

    # нажимаем кнопку, чтобы закрыть всплывающие окно, закрывающие доступ к сайту
    # todo catch если кнопку не одалось найти
    close_region_button = _driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/div/div/div/div/div/div/div/button')
    close_region_button.click()

    # вводим наименование продукта и нажимаем enter
    search_field_input = _driver.find_element(By.CLASS_NAME, 'search-field-input')
    search_field_input.send_keys(good_name)
    ActionChains(_driver).send_keys(Keys.ENTER).perform()

    time.sleep(5)

    minimum_price = 0
    medium_price = 0

    return medium_price, minimum_price


def start_megamarket_parsing():
    driver = driver_manager.create_driver()

    goods = ['"Телефон Apple iPhone 12 128Gb (Black)"']  # todo добавить чтение наименований из A1 столбца

    for good in goods:
        try:
            parse_prices(good, driver)
        except Exception as _ex:
            print(f"[SBERMEGAMARKET PARSER] Во время парсинга {_ex} возникла ошибка: {_ex}")

    driver_manager.kill_driver(driver)


start_megamarket_parsing()

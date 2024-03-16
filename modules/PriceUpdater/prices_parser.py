import re
# import os.path
# import time
# import pickle

import modules.PriceUpdater.driver_management as driver_management
import modules.GoogleSheets as gsheet
# from modules import BASE_DIR

# словарь с ключевыми данными для парсинга каждого сайта (полиморфизм на минималках)
sites_typeData = {'Store77': {'columnR': 'F', 'columnW': 'J', 'price_nameTag': 'p',
                              'price_class': 'price_title_product'},
                  'Sotohit': {'columnR': 'G', 'columnW': 'K', 'price_nameTag': 'div',
                              'price_class': 'price-current'},
                  'GSM': {'columnR': 'H', 'columnW': 'L', 'price_nameTag': 'span',
                          'price_class': 'product-price js-product-price'},
                  'ReStore': {'columnR': 'I', 'columnW': 'M', 'price_nameTag': 'div',
                              'price_class': 'detail-price__current'},
                  'Telegram': None,
                  'Megamarket': None}


# ПОЛУЧЕНИЕ ЦЕНЫ ТОВАРА С САЙТА
# принимает на вход драйвер с уже открытой страницей, а так же тип сайта, возвращает цену позиции на сайте,
# иначе вызывает исключение
def get_price(driver, site_type):
    soup = driver_management.get_htmlsoup(driver)
    # проверка на корректность переданного типа сайта
    if site_type not in sites_typeData:
        raise ValueError(f"[GET PRICE {site_type.upper()}] Ошибка! Некорректный тип сайта ({site_type}).")

    # словарь с ключевыми данными для парсинга текущего типа сайта
    siteData = sites_typeData[site_type]
    soup_match = soup.find(siteData.get('price_nameTag'), class_=siteData.get('price_class'))

    # если не была найдена цена - вызов ошибки с HTML кодом страницы и параметрами поиска
    if not soup_match:
        raise AttributeError(f'[GET PRICE {site_type.upper()}] Не удалось найти цену. '
                             f'Для {siteData.get("price_nameTag"), siteData.get("price_class")}\nMESSY URL:'
                             f' {driver.current_url}, {driver.page_source}')
    else:
        # находим только цифры в цене и возвращаем корректную цену без приколов с другими символами
        numbers = re.findall(r'\d+', soup_match.get_text())
        return float(''.join(numbers))


# ОБНОВЛЕНИЕ СТОЛБЦА ЦЕН В ГУГЛ ТАБЛИЦЕ
def update_prices(site_type):
    driver = driver_management.create_driver()
    driver.get('https://duckduckgo.com/')

    # задержка между обращениями к сайтам
    # time_delay = 2

    if site_type not in sites_typeData:
        raise Exception(f"[UPDATE PRICES {site_type.upper()}] Некорректно указан тип сайта для парсинга цен.")

    column = sites_typeData[site_type].get('columnR', None)

    # получаем из таблицы ссылки на товары
    urls = gsheet.read_column(column)[1:]
    # массив полученных цен
    upload_data = [[''] for _ in range(len(urls))]

    # итерация по URL-ам из таблицы
    for elem_id in range(len(urls)):
        url = urls[elem_id]
        try:
            # если нет URL
            if not url or url == 'нет':
                upload_data[elem_id] = ['не удалось найти ссылку на товар']
            # если URL присутствует
            else:
                # смена URL в текущем окне -> задержка (для минимизации шансов на блокировку и прогрузку страницы -----
                # -> вставка в массив цены, если она не была найдена, то вызовется обработка исключений и в массив будет
                # вставлено значение "ошибка"
                driver_management.switch_url(driver, url)
                # time.sleep(time_delay)
                upload_data[elem_id] = [get_price(driver, site_type)]
            print(f'[UPDATE PRICES {site_type.upper()}] Было получено значение цены: '
                  f'{upload_data[elem_id][0]}\nCURRENT URL: {url}')

        except Exception as _ex:
            print(f'[UPDATE PRICES {site_type.upper()}] Ошибка во время попытки получить цену товара ({_ex}).\n'
                  f'MESSY URL: {url}')
            upload_data[elem_id] = ['ошибка']

    # сохранение upload_data
    # with open(os.path.join(BASE_DIR, 'PriceUpdater', 'data', f"{site_type.lower()}.pkl"), "wb") as file:
    #     pickle.dump(upload_data, file)

    wr_column = sites_typeData[site_type].get('columnW', None)

    # запись по 100 позиций
    low_border = 0
    high_border = 50
    while high_border < len(upload_data) - 1:
        if high_border % 50 == 0:
            wr_range = f"{wr_column}{low_border + 2}:{wr_column}{high_border + 2}"
            gsheet.write_data(wr_range, upload_data[low_border:high_border + 1])
            low_border = high_border + 1

        high_border += 1

    wr_range = f"{wr_column}{low_border + 2}:{wr_column}{high_border + 2}"
    gsheet.write_data(wr_range, upload_data[low_border:high_border + 1])

    driver_management.kill_driver(driver)

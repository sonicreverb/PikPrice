import os.path
import re
import time
import pickle

import modules.PriceUpdater.driver_management as driver_management
import modules.GoogleSheets as gsheet
from modules import BASE_DIR

# словарь с ключевыми данными для парсинга каждого сайта (полиморфизм на минималках)
sites_typeData = {'Store77': {'columnR': 'F', 'columnW': 'J', 'price_nameTag': 'p',
                              'price_class': 'price_title_product'},
                  'Sotohit': {'columnR': 'G', 'columnW': 'K', 'price_nameTag': 'div',
                              'price_class': 'price-current'},
                  'GSM': {'columnR': 'H', 'columnW': 'L', 'price_nameTag': 'span',
                          'price_class': 'product-price js-product-price'},
                  'ReStore': {'columnR': 'I', 'columnW': 'M', 'price_nameTag': 'div',
                              'price_class': 'detail-price__current'}}


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
    time_delay = 2

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
    with open(os.path.join(BASE_DIR, 'PriceUpdater', 'data', f"{site_type.lower()}.pkl"), "wb") as file:
        pickle.dump(upload_data, file)

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

# TODO парсинг цен из телеграмм каналов
# принимает на вход словарь input_dict с наименованиями и ценами из прайс-листа в телеграмме, записывает неизвестные
# именования в файл, загружает цены в таблицу
# def upload_tginput1_prices(input_dict):
#     # массив с ценами, который будет загружён в таблицу в столбец J
#     upload_data = []
#     tginput1_names = read_column('C')[1:]
#
#     # проходимся по элементам tginput1_names, записываем цену для данного элемента в upload_data, если она есть, иначе
#     # добавляем в upload_data пустое место
#     for name in tginput1_names:
#         if name in input_dict:
#             upload_data.append([input_dict[name]])
#         else:
#             upload_data.append(['цена не найдена'])
#
#     # запись наименований, встречающихся в телеграм прайсе, но не находящихся в таблице
#     unknown_articles = []
#     for name_spc in input_dict:
#         if name_spc not in tginput1_names:
#             unknown_articles.append(name_spc)
#     print("Найдено " + str(len(unknown_articles)) + " неизвестных наименований в первом прайс-листе.")
#
#     # если найдено хотя бы одно неизвестное наименование
#     if len(unknown_articles) > 0:
#         with open(os.path.join(BASE_DIR, 'modules', 'PriceUpdater', 'unknown_articles1.txt'),
#                   'w', encoding='utf-8') as file_output:
#             for unkw_article in unknown_articles:
#                 file_output.write(unkw_article + '\n')
#
#     # запись upload_data в таблицу
#     service.spreadsheets().values().update(
#         spreadsheetId=spreadsheet_id,
#         range="M2:M",
#         valueInputOption="RAW",
#         body={'values': upload_data}
#     ).execute()
#
#
# # принимает на вход словарь input_dict с наименованиями и ценами из прайс-листа в телеграмме, записывает неизвестные
# # именования в файл, загружает цены в таблицу
# def upload_tginput2_prices(input_dict):
#     # массив с ценами, который будет загружён в таблицу в столбец J
#     upload_data = []
#     tginput2_names = read_column('D')[1:]
#
#     # проходимся по элементам tginput1_names, записываем цену для данного элемента в upload_data, если она есть, иначе
#     # добавляем в upload_data пустое место
#     for name in tginput2_names:
#         if name in input_dict:
#             upload_data.append([input_dict[name]])
#         else:
#             upload_data.append(['цена не найдена'])
#
#     # запись наименований, встречающихся в телеграм прайсе, но не находящихся в таблице
#     unknown_articles = []
#     for name_spc in input_dict:
#         if name_spc not in tginput2_names:
#             unknown_articles.append(name_spc)
#     print("Найдено " + str(len(unknown_articles)) + " неизвестных наименований во втором прайс-листе.")
#
#     # если найдено хотя бы одно наименование
#     if len(unknown_articles) > 0:
#         with open(os.path.join(BASE_DIR, 'modules', 'PriceUpdater', 'unknown_articles2.txt'),
#                   'w', encoding='utf-8') as file_output:
#             for unk_article in unknown_articles:
#                 file_output.write(unk_article + '\n')
#
#     # запись upload_data в таблицу
#     service.spreadsheets().values().update(
#         spreadsheetId=spreadsheet_id,
#         range="N2:N",
#         valueInputOption="RAW",
#         body={'values': upload_data}
#     ).execute()
#
#
# # запускает обработку файлов с товарами из прайс-листа тг и их загрузку в таблицу
# def upload_tg_prices(input_dict1, input_dict2):
#     upload_tginput1_prices(input_dict1)
#     upload_tginput2_prices(input_dict2)

import os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from modules.PriceUpdater.parser import parse_price
from bot.create_bot import BASE_DIR

spreadsheet_id = '1j6iPfQH1sd3Xw3ZVI_RdN5Nb52buWoH0SPMJUR-2tdo'
sheet_name = 'catalog'

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
sacc_json_path = os.path.join(BASE_DIR, 'modules', 'GoogleSheets', 'creds', 'sacc1.json')

credentials = ServiceAccountCredentials.from_json_keyfile_name(sacc_json_path, scope)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()


# считывает столбец из таблицы по его литералу, возвращает массив значений
def read_column(column_name):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=sheet_name+'!'+column_name+':'+column_name).execute()

    values = []
    for value in result.get('values'):
        values.append(value[0])

    return values


# считывает из таблицы столбец ссылок, после чего заполняет массив ценами товаров, загружает цены в таблицу
def upload_store77_prices():
    # массив с ценами, который будет загружён в таблицу в столбец H
    upload_data = []
    store77links = read_column('F')[1:]

    for link in store77links:
        try:
            if link == 'нет':
                upload_data.append(['ссылка на товар не найдена'])
            else:
                upload_data.append([parse_price(link, 'store77')])
        except Exception as _ex:
            upload_data.append(['ошибка'])
            print(f'[UPLOAD STORE77 PRICES] Ошибка при попытке обновить цену товара - {link}\n {_ex}')

    # запись upload_data в таблицу
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="I2:I",
        valueInputOption="RAW",
        body={'values': upload_data}
    ).execute()


# считывает из таблицы столбец ссылок, после чего заполняет массив ценами товаров, загружает цены в таблицу
def upload_sotohit_prices():
    # массив с ценами, который будет загружён в таблицу в столбец I
    upload_data = []
    sotolinks = read_column('G')[1:]

    for link in sotolinks:
        try:
            if link == 'нет':
                upload_data.append(['ссылка на товар не найдена'])
            else:
                upload_data.append([parse_price(link, 'sotohit')])
        except Exception as _ex:
            upload_data.append(['ошибка'])
            print(f'[UPLOAD SOTOHIT PRICES] Ошибка при попытке обновить цену товара - {link}\n {_ex}')

    # запись upload_data в таблицу
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="J2:J613",
        valueInputOption="RAW",
        body={'values': upload_data}
    ).execute()


# считывает из таблицы столбец ссылок, после чего заполняет массив ценами товаров, загружает цены в таблицу
def upload_gsm_prices():
    # массив с ценами, который будет загружён в таблицу в столбец I
    upload_data = []
    gsm_links = read_column('H')[1:]

    for link in gsm_links:
        print(link)
        try:
            if link == 'нет':
                upload_data.append(['ссылка на товар не найдена'])
            else:
                upload_data.append([parse_price(link, 'gsm')])
        except Exception as _ex:
            upload_data.append(['ошибка'])
            print(f"[UPLOAD GSM PRICES] Ошибка при попытке обновить цену товара - {link}\n {_ex}")
    # запись upload_data в таблицу
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="K2:K",
        valueInputOption="RAW",
        body={'values': upload_data}
    ).execute()


# принимает на вход словарь input_dict с наименованиями и ценами из прайс-листа в телеграмме, записывает неизвестные
# именования в файл, загружает цены в таблицу
def upload_tginput1_prices(input_dict):
    # массив с ценами, который будет загружён в таблицу в столбец J
    upload_data = []
    tginput1_names = read_column('C')[1:]

    # проходимся по элементам tginput1_names, записываем цену для данного элемента в upload_data, если она есть, иначе
    # добавляем в upload_data пустое место
    for name in tginput1_names:
        if name in input_dict:
            upload_data.append([input_dict[name]])
        else:
            upload_data.append(['цена не найдена'])

    # запись наименований, встречающихся в телеграм прайсе, но не находящихся в таблице
    unknown_articles = []
    for name_spc in input_dict:
        if name_spc not in tginput1_names:
            unknown_articles.append(name_spc)
    print("Найдено " + str(len(unknown_articles)) + " неизвестных наименований в первом прайс-листе.")

    # если найдено хотя бы одно неизвестное наименование
    if len(unknown_articles) > 0:
        with open(os.path.join(BASE_DIR, 'modules', 'PriceUpdater', 'unknown_articles1.txt'),
                  'w', encoding='utf-8') as file_output:
            for unkw_article in unknown_articles:
                file_output.write(unkw_article + '\n')

    # запись upload_data в таблицу
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="L2:L",
        valueInputOption="RAW",
        body={'values': upload_data}
    ).execute()


# принимает на вход словарь input_dict с наименованиями и ценами из прайс-листа в телеграмме, записывает неизвестные
# именования в файл, загружает цены в таблицу
def upload_tginput2_prices(input_dict):
    # массив с ценами, который будет загружён в таблицу в столбец J
    upload_data = []
    tginput2_names = read_column('D')[1:]

    # проходимся по элементам tginput1_names, записываем цену для данного элемента в upload_data, если она есть, иначе
    # добавляем в upload_data пустое место
    for name in tginput2_names:
        if name in input_dict:
            upload_data.append([input_dict[name]])
        else:
            upload_data.append(['цена не найдена'])

    # запись наименований, встречающихся в телеграм прайсе, но не находящихся в таблице
    unknown_articles = []
    for name_spc in input_dict:
        if name_spc not in tginput2_names:
            unknown_articles.append(name_spc)
    print("Найдено " + str(len(unknown_articles)) + " неизвестных наименований во втором прайс-листе.")

    # если найдено хотя бы одно наименование
    if len(unknown_articles) > 0:
        with open(os.path.join(BASE_DIR, 'modules', 'PriceUpdater', 'unknown_articles2.txt'),
                  'w', encoding='utf-8') as file_output:
            for unk_article in unknown_articles:
                file_output.write(unk_article + '\n')

    # запись upload_data в таблицу
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="M2:M",
        valueInputOption="RAW",
        body={'values': upload_data}
    ).execute()


# запускает обработку файлов с товарами из прайс-листа тг и их загрузку в таблицу
def upload_tg_prices(input_dict1, input_dict2):
    upload_tginput1_prices(input_dict1)
    upload_tginput2_prices(input_dict2)
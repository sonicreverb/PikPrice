import os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from bot.modules.price_parser.parser import parse_price
from bot.create_bot import BASE_DIR

spreadsheet_id = '1j6iPfQH1sd3Xw3ZVI_RdN5Nb52buWoH0SPMJUR-2tdo'
sheet_name = 'catalog'

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
sacc_json_path = os.path.join(BASE_DIR, 'bot', 'modules', 'tables', 'creds', 'sacc1.json')

credentials = ServiceAccountCredentials.from_json_keyfile_name(sacc_json_path, scope)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()


def read_column(column_name):
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=sheet_name+'!'+column_name+':'+column_name).execute()

    values = []
    for value in result.get('values'):
        values.append(value[0])

    return values


def upload_store77_prices():
    # массив с ценами, который будет загружён в таблицу в столбец H
    upload_data = []
    store77links = read_column('F')[1:]

    for link in store77links:
        if link == 'нет':
            upload_data.append(['ссылка на товар не найдена'])
        else:
            upload_data.append([parse_price(link, 'store77')])

    # запись upload_data в таблицу
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="H2:H613",
        valueInputOption="RAW",
        body={'values': upload_data}
    ).execute()


def upload_sotohit_prices():
    # массив с ценами, который будет загружён в таблицу в столбец I
    upload_data = []
    store77links = read_column('G')[1:]

    for link in store77links:
        if link == 'нет':
            upload_data.append(['ссылка на товар не найдена'])
        else:
            upload_data.append([parse_price(link, 'sotohit')])

    # запись upload_data в таблицу
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="I2:I613",
        valueInputOption="RAW",
        body={'values': upload_data}
    ).execute()


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
            upload_data.append(['цена не найдена, либо ошибка именования'])

    # запись наименований, встречающихся в телеграм прайсе, но не находящихся в таблице
    unknown_articles = []
    for name_spc in input_dict:
        if name_spc not in tginput1_names:
            unknown_articles.append(name_spc)
    print("Найдено " + str(len(unknown_articles)) + " неизвестных наименований в первом прайс-листе.")

    # если найдено хотя бы одно наименование
    if len(unknown_articles) > 0:
        with open(os.path.join(BASE_DIR, 'bot', 'modules', 'input_price', 'unknown_articles1.txt'),
                  'w', encoding='utf-8') as file_output:
            for unkw_article in unknown_articles:
                file_output.write(unkw_article + '\n')

    # запись upload_data в таблицу
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="J2:J613",
        valueInputOption="RAW",
        body={'values': upload_data}
    ).execute()


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
            upload_data.append(['цена не найдена, либо ошибка именования'])

    # запись наименований, встречающихся в телеграм прайсе, но не находящихся в таблице
    unknown_articles = []
    for name_spc in input_dict:
        if name_spc not in tginput2_names:
            unknown_articles.append(name_spc)
    print("Найдено " + str(len(unknown_articles)) + " неизвестных наименований во втором прайс-листе.")

    # если найдено хотя бы одно наименование
    if len(unknown_articles) > 0:
        with open(os.path.join(BASE_DIR, 'bot', 'modules', 'input_price', 'unknown_articles2.txt'),
                  'w', encoding='utf-8') as file_output:
            for unk_article in unknown_articles:
                file_output.write(unk_article + '\n')

    # запись upload_data в таблицу
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="K2:K613",
        valueInputOption="RAW",
        body={'values': upload_data}
    ).execute()


def upload_all_prices(input_dict1, input_dict2):
    # upload_store77_prices()
    # upload_sotohit_prices()
    upload_tginput1_prices(input_dict1)
    upload_tginput2_prices(input_dict2)


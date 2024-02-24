import os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from modules import BASE_DIR

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
        if value:
            values.append(value[0])
        else:
            values.append('')

    return values


# делает запись массива upload_data в таблицу, wr_range формата "J2:J100" или же "J2:J" если неизвестен индекс
# последнего элемента
def write_data(wr_range, upload_data):
    # запись upload_data в таблицу
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=wr_range,
        valueInputOption="RAW",
        body={'values': upload_data}
    ).execute()

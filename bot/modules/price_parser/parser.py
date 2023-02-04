import requests
from bs4 import BeautifulSoup
# import time
# import os
# from bot.create_bot import BASE_DIR
# import json as js
# from openpyxl import load_workbook


def get_html(url):
    r = requests.get(url, verify=False)
    return r


def get_price(html, site_type):
    if site_type == 'store77':
        soup = BeautifulSoup(html, 'html.parser')
        price = soup.find('p', class_='price_title_product').get_text()[:-2].split()
        price = price[0] + price[1]
        return price
    elif site_type == 'sotohit':
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h1').get_text()
        title_spc = ''.join(title.split()).upper()
        price = soup.find('div', class_='price-current').get_text()[1:-3]
        return price


def parse_price(url, site_type):
    html = get_html(url)
    if html.status_code == 200:
        try:
            result = get_price(html.text, site_type)
            return result
        except AttributeError:
            print('AttributeError in parser.py line 33', url)
            return 'error'

    else:
        print('Warning HTMl status code 418 parser.py line 30 ', url)
        return 'invalid url'


# def automatic_parser():
#     wb = load_workbook(os.path.join(BASE_DIR, 'bot', 'modules', 'tables', 'table_pikprice.xlsx'))
#     ws = wb['data']
#     line = 2
#x`
#     store_dict = {}
#     stoma_dict = {}
#
#     while line <= wb.worksheets[0].max_row:
#         title = ws["A" + str(line)].value
#         pik_article = ws["D" + str(line)].value
#         if title:
#             if pik_article != "нет":
#                 link_store = ws["F" + str(line)].value
#                 link_stoma = ws["G" + str(line)].value
#                 if link_store != "нет":
#                     store_dict[pik_article] = parse(link_store, "store")
#                 if link_stoma != "нет":
#                     stoma_dict[pik_article] = parse(link_stoma, "stoma")
#         line += 1
#         print(store_dict, stoma_dict)
#     wb.close()
#
#     with open(os.path.join(BASE_DIR, 'bot', 'modules', 'price_parser', 'jsondir', 'jsonstore.txt'),
#               'w', encoding='utf-8') as json_file:
#         js.dump(store_dict, json_file, ensure_ascii=False)
#
#     with open(os.path.join(BASE_DIR, 'bot', 'modules', 'price_parser', 'jsondir', 'jsonstoma.txt'),
#               'w', encoding='utf-8') as json_file:
#         js.dump(stoma_dict, json_file, ensure_ascii=False)


#automatic_parser()
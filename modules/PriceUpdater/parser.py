import requests
import re
from bs4 import BeautifulSoup


# возвращает html (reguest.get) указанного url'a
def get_html(url):
    r = requests.get(url, verify=False)
    return r


# принимает на вход html и тип сайта, парсит и возвращает цену позиции
def get_price(html, site_type):
    soup = BeautifulSoup(html, 'html.parser')

    if site_type == 'store77':
        soup = BeautifulSoup(html, 'html.parser')
        split_price = soup.find('p', class_='price_title_product').get_text().split()
        price = ''
        for tmp in range(len(split_price) - 1):
            price = price + split_price[tmp]
        return price

    elif site_type == 'sotohit':
        price = soup.find('div', class_='price-current').get_text()[1:-3]
        return price

    elif site_type == 'gsm':
        split_price = soup.find('span', class_='product-price js-product-price').get_text().split()
        price = ''
        for tmp in range(len(split_price) - 1):
            price = price + split_price[tmp]
        return price


# принимает на вход url товара и тип сайта, получает html, вызывает get_price() и возвращает цену позиции
def parse_price(url, site_type):
    html = get_html(url)
    if html.status_code == 200:
        try:
            result = get_price(html.text, site_type)
            print(f"[{site_type.upper()}] {url} - {result}")
            if result == '':
                return 'none'
            return result
        except AttributeError:
            print('AttributeError in parser.py line 33', url)
            return 'error'

    else:
        print(f'[{site_type.upper()}] Warning HTMl status code 418 parser.py line 30 {url}')
        return 'invalid url'


# форматирует входные данные (прайс-листы) из телеграмм каналов и возвращает словарь с наименованием товара[цена товара]
def format_inputprice(textinput):
    # разделяем сплошной текст на строки (каждая строка - один товар), заполняем им массив
    text_lines_li = textinput.split('\n')
    # если в строке будут эти эмодзи, значит эта строка содержит товар
    emojiflag_li = ['🇮🇳', '🇪🇺', '🇬🇧', '🇺🇸', '🇯🇵', '🇷🇺', '🇦🇪', '🇭🇰', '🇰🇿', '🇰🇷', '📺', '🎮', '🔌', '🔋', '🖱']
    name_spc_dict = {}

    for line in text_lines_li:
        for emoji_flag in emojiflag_li:
            if emoji_flag in line:
                try:
                    price = re.search(r'\d{4,6}', line)[0]
                    name = line.split()
                    name = ''.join(name)

                    # при помощи проверки находим, как в строке поставщик разделил название и цену, чтобы правильно её
                    # сформировать
                    if name[0:name.index('-')]:
                        name_spc = name[0:name.index('-')].upper()
                    elif name[0:name.index('.')]:
                        name_spc = name[0:name.index('.')].upper()
                    else:
                        continue

                    if name_spc in name_spc_dict:
                        if price < name_spc_dict[name_spc]:
                            name_spc_dict[name_spc] = price
                    else:
                        name_spc_dict[name_spc] = price

                except AttributeError:
                    print("AttributeError in try statement, parser.py; format_input_price()", line)
                except TypeError:
                    print("TypeError in try statement, parser.py; format_input_price()", line)

    return name_spc_dict

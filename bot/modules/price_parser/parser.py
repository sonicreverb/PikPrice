import requests
from bs4 import BeautifulSoup


def get_html(url):
    r = requests.get(url, verify=False)
    return r


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

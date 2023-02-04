import requests
from bs4 import BeautifulSoup


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

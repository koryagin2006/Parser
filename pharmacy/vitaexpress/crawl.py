from pathlib import Path
import codecs
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import pandas as pd
import json
import time
import math
import urllib.parse
from datetime import datetime

host = 'https://vitaexpress.ru'
result_path = 'result/%s' % datetime.today().date()

Path(result_path).mkdir(parents=True, exist_ok=True)

def parse_product(product, city_title):
    def parse_price(price):
        if price == None:
            return '0'

        price_parts = []
        for child in price.children:
            if isinstance(child, Tag):
                if 'priceSVG__num' in child.get('class'):
                    price_parts.append(price_convert_map[child.find('use').attrs['xlink:href'].split('-')[-1]])

                if 'priceSVG__separ' in child.get('class'):
                    price_parts.append('.')

        return ''.join(price_parts)

    title = product.find('span', {'itemprop': 'name'})

    print(title.text)
    if title == None:
        return

    price = product.find('span', {'class': 'priceSVG'})
    if price == None:
        return

    price_convert_map = {
        '0': '5',
        '1': '9',
        '2': '7',
        '3': '6',
        '4': '4',
        '5': '0',
        '6': '8',
        '7': '2',
        '8': '3',
        '9': '1',
    }
    price = parse_price(price)
    price_old = parse_price(product.find('span', {'class': 'priceSVG--old'}))

    print(price, price_old)

    return pd.DataFrame([[city_title, title.text, price_old != '0', price, price_old]], columns = ['city', 'title', 'sale', 'price', 'price_old'])

def parse_category(df, user_city, city, category_def):
    def grep(page_href):
        print(page_href)

        session = requests.Session()
        session.head(page_href)

        r = session.get(
            url=page_href,
            data={},
            headers={
                'Referer': page_href,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
            },
            cookies={
                'PHPSESSID': '88q1opk94tui4ql64jglpgptpm',
                'user_city': user_city,
                'list-city': '1',
                'info-sticky': '1',
                'BX_USER_ID': '18474e0c50cb5c8c84f9e1964f792606',
                'TS2fa81da0029=08988fd746ab2800c55e70f1e0c6b2aa2f1234207a694f7631cb7fb936cbaa80f44b8e5c51f081c1448206ac8e6b876e': ''
            }
        )
        catalog = BeautifulSoup(r.text, features='html.parser')

        return {
            'products': catalog.find_all('div', {'class': 'product'}),
            'last': catalog.find('a', {'class': 'js-pager-next'}) == None
        }

    max_page = math.ceil(category_def['max'] / 24)
    last_product = None

    for i in range(0, max_page):
        data = grep('%s/ajax/filter.php?sort=PROPERTY_CATALOG_SORT&direction=DESC&filters=%d&brands=&props=&gamma=&PAGEN_2=%d&PAGEN_1=%d&subsect=&sect=&min=0&max=%d&menuSection=&gammaShow=N&brandCode=&landingCode=&tagCode=' % (host, category_def['id'], i + 1, i, category_def['max']))

        if len(data['products']) == 0:
            break

        last_product_id = data['products'][-1].attrs['data-id']
        if last_product == last_product_id:
            break

        last_product = last_product_id
        for product in data['products']:
            df = df.append(parse_product(product, city), ignore_index=True)

        df.to_csv('%s/%s.csv' % (result_path, city))
        time.sleep(.5)

    return df

cities = {
    'Астрахань': '%7B%22id%22%3A%2299385%22%2C%22name%22%3A%22%5Cu0410%5Cu0441%5Cu0442%5Cu0440%5Cu0430%5Cu0445%5Cu0430%5Cu043d%5Cu044c%22%7D'
}

cats = {
    '836': '4297', '3706': '6297', '804': '2135', '1121': '10419', '877': '14300', '1244': '3729', '1167': '6159', '898': '23244', '911': '25600', '1128': '6990', '1154': '19979',
    '920': '3769', '1158': '2515', '1035': '117810', '1028': '8226', '1086': '30769', '1132': '14897', '1101': '4338', '963': '229', '1172': '40500', '860': '13477', '1214': '2868', '1024': '10150', '1148': '120156', '1230': '10197', '931': '999', '2446': '8010', '2458': '5431', '2488': '5020', '2551': '4769', '2567': '8620', '2586': '3179', '3730': '1609', '3735': '1799', '1248': '418', '2863': '2699', '2879': '1749', '2888': '4939', '2944': '2099', '2947': '8639', '2951': '2519', '2977': '1919', '2983': '407', '2986': '2409', '3011': '723', '990': '4001', '996': '7049', '1001': '4800', '1002': '8340', '1005': '14309', '1011': '5820', '1012': '9059', '1013': '779', '1014': '57241', '1015': '399',
    '3715': '4297', '3718': '36518', '3719': '914', '1187': '4100', '1189': '3860', '1190': '5780', '1191': '13719', '1192': '13690', '1198': '5489', '1199': '8690', '1200': '10799', '1207': '3015', '3708': '11299', '3709': '16890'
}

for city in cities:
    result = pd.DataFrame()
    for cat_id in cats:
        result = parse_category(result, cities[city], city, {
            'id': int(cat_id),
            'max': int(cats[cat_id]),
        })


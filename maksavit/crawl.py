from pathlib import Path
import codecs
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

host = 'https://maksavit.ru'
data_url = host + '/ajax/goals.php'

Path('result').mkdir(parents=True, exist_ok=True)

def parse_product(city_id, id):
    session = requests.Session()
    session.head(data_url)
    print(data_url)
    prices = session.post(
        url=data_url,
        data={
            'PRODUCT_ID': id,
            'PRICE_ID': '58bf45a5-9daa-11e5-a855-00155d000316_P',
            'session_id': '4a18da164309f2f44f934220c01484f3'
        },
        headers={
            'Referer': 'https://maksavit.ru/catalog/94342/',
            'x-requested-with': 'XMLHttpRequest',
            'Origin': 'https://maksavit.ru'
        },
        cookies={
            'current_region': city_id,
            'BITRIX_SM_SALE_UID': '9bde4625bc25fdcc51185147f77e7e29',
            'datePopup': '10.06.2020'
        }
    )

    json_string = json.dumps(prices.text)
    print(json_string)

    #return pd.DataFrame([[city, title.text, min_price, max_price]], columns = ['city', 'title', 'price_min', 'price_max'])

# 'orenburg',
cities = {136356: 'Архангельск'}

parse_product('136356', '94342')

"""for city_id in cities:
    result = pd.DataFrame()
    for id in range(0, 35000):
        print(city, id)
        result = result.append(parse_product(city, id), ignore_index=True)
        result.to_csv('result/%s.csv' % city)

        time.sleep(3)
"""

"""
r = requests.get(url + '/catalog')
with codecs.open('raw/catalog.html', 'w', 'utf-8') as output_file:
    output_file.write(r.text)

catalog = BeautifulSoup(r.text, features='html.parser')
category_links = catalog.find('div', {'class': 'catalog-categories'}).find_all('a')

for link in category_links:
    print(link.get('href'))
    print(link.text)


def parse_category(category_link):
    res = pd.DataFrame()
"""

"""
prices_url = '%s/ajax/product-map?id=%d' % (host, id)

    session = requests.Session()
    session.head(prices_url)

    prices = session.get(
        url=prices_url,
        data={},
        headers={
            'Referer': url,
            'x-requested-with': 'XMLHttpRequest'
        }
    )

    json_string = json.dumps(prices.text)
    print(json_string)
"""

"""
html = requests.get('%s/%s/product/%d' % (host, city, id))
    product = BeautifulSoup(html.text, features='html.parser')

    title = product.find('h1', {'class': 'title'})
    if title == None:
        return

    price_block = product.find('div', {'id': 'variants'})
    if price_block == None:
        return

    items = price_block.find_all('div', {'class': 'pv-item'})
    value = price_block.find('meta', {'itemprop': 'price'})

    if value == None:
        return

    prices = [item['data-price'] for item in price_block.find_all('div', attrs={'data-price' : True})]
    min_price = min(prices)
    max_price = max(prices)
"""

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
    def parse_price(price_block):
        if price_block == None:
            return '0'
        else:
            return price_block.text.replace('от', '').replace('₽', '').replace(' ', '').strip()

    title = product.find('span', {'itemprop': 'name'})

    print(title.text)
    if title == None:
        return

    price = parse_price(product.find('div', {'itemprop': 'price'}))
    if price == '0':
        return

    price_old = parse_price(product.find('div', {'class': 'product-card__price-old'}))

    return pd.DataFrame([[city_title, title.text, price_old != '0', price, price_old]], columns = ['city', 'title', 'sale', 'price', 'price_old'])

def parse_category(df, city_id, city, category_href):
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
                'city_id': city_id
            }
        )
        catalog = BeautifulSoup(r.text, features='html.parser')
        active_page = catalog.find('span', {'class': 'pagination__item_active'})

        return {
            'products': catalog.find_all('div', {'class': 'product-card'}),
            'last': active_page == None or active_page.next_sibling == None
        }

    page = 1
    while True:
        data = grep('%s?PAGEN_1=%d' % (category_href, page))

        if len(data['products']) == 0 or data['last']:
            break

        for product in data['products']:
            df = df.append(parse_product(product, city), ignore_index=True)

        df.to_csv('%s/%s.csv' % (result_path, city))
        time.sleep(2)

        page += 1

    return df

with open('categories.json', encoding='utf-8') as categories_file:
    categories = json.load(categories_file)

with open('cities.json', encoding='utf-8') as cities_file:
    cities = json.load(cities_file)

for city in cities:
    result = pd.DataFrame()
    start = time.time()
    for category in categories:
        result = parse_category(result, city['id'], city['label'], category['href'])

    with open('result/time.txt', 'a') as file:
        file.write('%s crawl time %f\n' % (city, time.time() - start))
        file.close()


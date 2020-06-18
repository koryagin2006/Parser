from pathlib import Path
import codecs
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import time

host = 'https://6030000.ru/'
result_path = 'result/%s' % datetime.today().date()

def parse_product(product, city_title):
    if product == None:
        return

    title = product.attrs['data-name']
    if title == None:
        return

    price = product.attrs['data-price']
    if price == None:
            return

    print(title, price)

    return pd.DataFrame([[city_title, title.strip(), price, price]], columns = ['city', 'title', 'price_min', 'price_max'])


def parse_category(df, city_id, city, category_href):
    page_size = 54

    def grep(page_href):
        r = requests.get(page_href, cookies={'SELECTED_CITY': city_id})
        catalog = BeautifulSoup(r.text, features='html.parser')
        list = catalog.find('div', {'class': 'catalogue-group__content'})

        if list == None:
            print('No .catalogue-group__content found')
            return {
                'products': [],
                'last': True
            }

        products = list.find_all('div', {'class': 'product_data'})
        links = catalog.find_all('a', {'class': 'pagination__item_inactive'})
        last = len(products) < page_size or len(links) == 2

        return {
            'products': products,
            'last': last
        }

    r = requests.get(category_href)
    page = BeautifulSoup(r.text, features='html.parser')

    for i in range(1, 100):
        url = '%s?ORDER=desc&PAGE_SIZE=%d&PAGE=%d' % (category_href, page_size, i)
        print(url)
        data = grep(url)

        for product in data['products']:
            df = df.append(parse_product(product, city), ignore_index=True)

        df.to_csv('%s/%s.csv' % (result_path, city))
        time.sleep(3)

        if data['last']:
            return df

    return df

Path(result_path).mkdir(parents=True, exist_ok=True)

with open('categories.json', encoding='utf-8') as categories_file:
    categories = json.load(categories_file)

with open('cities.json', encoding='utf-8') as cities_file:
    cities = json.load(cities_file)

for city in cities:
    result = pd.DataFrame()
    for category in categories:
        result = parse_category(result, city['id'], city['text'], category['href'])

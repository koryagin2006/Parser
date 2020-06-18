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

host = 'https://apteka-april.ru'
result_path = 'result/%s' % datetime.today().date()

Path(result_path).mkdir(parents=True, exist_ok=True)

def parse_product(product, city_title):
    price = product['price']
    return pd.DataFrame([[city_title, product['name'], price['withCard'] != price['withoutCard'], price['withCard'], price['withoutCard']]], columns = ['city', 'title', 'sale', 'price', 'price_old'])

def parse_category(df, city_id, city_title, typeID, subtypeID):
    def grep(page_href):
        print(page_href)

        session = requests.Session()
        session.head(page_href)

        r = session.get(
            url=page_href,
            data={},
            headers={
                'Origin': host,
                'Referer': page_href,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
            },
        )

        return json.loads(r.text)

    offset = 0
    while True:
        products = grep('https://api.apteka-april.ru/catalog/ID,price,sticker,name@products?typeIDs=%s&subtypeIDs=%s&cityID=%s:-averageRating[%d:23]'  % (typeID, subtypeID, city_id, offset))

        if products == None:
            break

        if len(products) > 0:
            for product in products:
                df = df.append(parse_product(product, city_title), ignore_index=True)

            df.to_csv('%s/%s.csv' % (result_path, city_title))
            time.sleep(1)

        if len(products) < 23:
            break

        offset += 23

    return df

with open('categories.json', encoding='utf-8') as categories_file:
    categories = json.load(categories_file)

with open('cities.json', encoding='utf-8') as cities_file:
    cities = json.load(cities_file)

for city in cities:
    result = pd.DataFrame()
    start = time.time()
    for category in categories:
        cat_ids = category['ids']
        result = parse_category(result, city['id'], city['title'], cat_ids[0], cat_ids[1])

    with open('result/time.txt', 'a') as file:
        file.write('%s crawl time %f\n' % (city['title'], time.time() - start))
        file.close()

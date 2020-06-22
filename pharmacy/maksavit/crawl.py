from pathlib import Path
import codecs
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime

host = 'https://maksavit.ru'
data_url = host + '/catalog/%s/'
result_path = 'result/%s' % datetime.today().date()

Path(result_path).mkdir(parents=True, exist_ok=True)

def get_html(url, city_id):
    session = requests.Session()
    session.head(url)

    r = session.get(
        url=url,
        data={},
        headers={
            'Referer': url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
        },
        cookies={
            'current_region': city_id
        }
    )

    return r.text

def parse_product(city_id, city, id):
    html = get_html(data_url % id, city_id)
    if html == None:
        return

    print(data_url % id)

    dom = BeautifulSoup(html, features='html.parser')

    title = dom.find('h1')
    price_block = dom.find('div', {'class': 'pharmacies_block'})
    if title == None or price_block == None:
        return

    price_items = price_block.find_all('div', {'class': 'item__position-wrap'})
    prices = []
    for item in price_items:
        prices.append(item.find('div', {'class': 'price'}).text.replace(' ', '').replace('р.', '').strip())

    return pd.DataFrame([[city, title.text, min(prices), max(prices)]], columns = ['city', 'title', 'price_min', 'price_max'])

with open('cities.json', encoding='utf-8') as cities_file:
    cities = json.load(cities_file)

for city in cities:
    result = pd.DataFrame()
    start = time.time()
    for id in range(700, 100000):
        result = result.append(parse_product(city['id'], city['name'], id), ignore_index=True)
        result.to_csv('%s/%s.csv' % (result_path, city['name']))
        time.sleep(2)

    with open('result/time.txt', 'a') as file:
        file.write('%s crawl time %f\n' % (city['name'], time.time() - start))
        file.close()

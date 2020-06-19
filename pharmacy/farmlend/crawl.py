from pathlib import Path
import codecs
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime

host = 'https://farmlend.ru'
result_path = 'result/%s' % datetime.today().date()

Path(result_path).mkdir(parents=True, exist_ok=True)

def parse_product(city, id):
    html = requests.get('%s/%s/product/%d' % (host, city, id))
    product = BeautifulSoup(html.text, features='html.parser')
    res = pd.DataFrame()

    title = product.find('h1', {'class': 'title'})
    if title == None:
        return res

    price_block = product.find('div', {'id': 'variants'})
    if price_block == None:
        return res

    items = price_block.find_all('div', {'class': 'pv-item'})
    value = price_block.find('meta', {'itemprop': 'price'})

    if value == None:
        return res

    prices = [item['data-price'] for item in price_block.find_all('div', attrs={'data-price' : True})]
    min_price = min(prices)
    max_price = max(prices)

    return res.append(pd.DataFrame([[city, title.text, min_price, max_price]], columns = ['city', 'title', 'price_min', 'price_max']), ignore_index=True)

cities = [
    'orenburg', 'samara', 'ekaterinburg', 'tyumen', 'chelyabinsk',
    'ufa', 'kazan' 'izhevsk',
    'orsk', 'buzuluk', 'neftekamsk', 'sterlitamak', 'bugulma',
    'tyumen', 'naberezhnye-chelny', 'sarapul', 'votkinsk',
    'tolyatti', 'nizhnii-tagil', 'verhnyaya-salda', 'zlatoust', 'magnitogorsk'
]

results = {}
for id in range(0, 40500):
    start = time.time()

    for city in cities:
        if city not in results:
            results[city] = pd.DataFrame()

        product = parse_product(city, id)
        if product.empty:
            print('Skip', city, id)
            if city == 'orenburg':
                break
            else:
                continue

        print(city, id)
        results[city] = results[city].append(product, ignore_index=True)
        results[city].to_csv('%s/%s.csv' % (result_path, city))
        time.sleep(.3)

    with open('result/time.txt', 'a') as file:
    	file.write('%d crawl time %f\n' % (id, time.time() - start))
    	file.close()


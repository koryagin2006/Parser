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

    res = pd.DataFrame()
    return res.append(pd.DataFrame([[city, title.text, min_price, max_price]], columns = ['city', 'title', 'price_min', 'price_max']), ignore_index=True)

cities = [
    'samara', 'ekaterinburg', 'tyumen', 'chelyabinsk',
    'orenburg', 'ufa', 'kazan' 'izhevsk',
    'orsk', 'buzuluk', 'neftekamsk', 'sterlitamak', 'bugulma',
    'tyumen', 'naberezhnye-chelny', 'sarapul', 'votkinsk',
    'tolyatti', 'nizhnii-tagil', 'verhnyaya-salda', 'zlatoust', 'magnitogorsk'
]


for city in cities:
    result = pd.DataFrame()
    start = time.time()
    for id in range(0, 40500):
        print(city, id)
        result = result.append(parse_product(city, id), ignore_index=True)
        result.to_csv('%s/%s.csv' % (result_path, city))

        time.sleep(.3)

    with open('result/time.txt', 'a') as file:
    	file.write('%s crawl time %f\n' % (city, time.time() - start))
    	file.close()


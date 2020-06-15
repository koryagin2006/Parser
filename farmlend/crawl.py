from pathlib import Path
import codecs
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

host = 'https://farmlend.ru'

Path('raw').mkdir(parents=True, exist_ok=True)
Path('result').mkdir(parents=True, exist_ok=True)

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

# 'orenburg', 'ufa', 'kazan' 'izhevsk'
# 'samara', 'ekaterinburg', 'tyumen', 'chelyabinsk'

# 'orsk', 'buzuluk', 'neftekamsk', 'sterlitamak', 'naberezhnye-chelny', 'bugulma', 'sarapul', 'votkinsk'
# 'tolyatti', 'nizhnii-tagil', 'verhnyaya-salda', 'zlatoust', 'magnitogorsk'
cities = [ 'tyumen', 'orsk', 'buzuluk', 'neftekamsk', 'sterlitamak', 'naberezhnye-chelny', 'bugulma', 'sarapul', 'votkinsk' ]

for city in cities:
    result = pd.DataFrame()
    for id in range(0, 40500):
        print(city, id)
        result = result.append(parse_product(city, id), ignore_index=True)
        result.to_csv('result/%s.csv' % city)

        time.sleep(.3)


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

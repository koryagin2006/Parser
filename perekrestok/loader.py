import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from random import choice
from multiprocessing import Pool

ORIGIN = 'https://www.perekrestok.ru'
useragents = open('../useragents.txt').read().split('\n')

def get_html(url, headers):
    r = requests.get(url, headers=headers)
    return r.text


def get_product(product):
    name = product.split('/')[-1].strip()
    html = get_html(ORIGIN + product, {'User-Agent': choice(useragents)})	
    with open('raw/products/' + name, 'w') as file:
	file.write(html.encode('utf-8'))
	file.close()


def main():
    products = open('raw/products.txt').read().split('\n')
    pool = Pool(20)
    pool.map(get_product, products)


if __name__ == '__main__':
    main()

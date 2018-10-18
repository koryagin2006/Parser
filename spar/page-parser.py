# -*- coding: utf-8 -*-
import csv
import requests
from bs4 import BeautifulSoup
from random import choice
from multiprocessing import Pool
from PIL import Image
from os import listdir
from os.path import isfile, join

ORIGIN = 'https://www.auchan.ru/'
BASE = 'raw/products'
useragents = open('../useragents.txt').read().split('\n')

csvfile = open('result/data.csv', 'w')
fieldnames = ['id', 'title', 'category', 'subcategory', 'price', 'brand', 'manufacturer', 'code', 'description', 'text', 'img_src', 'source']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()


def get_meta(soup, name):
    metas = soup.find_all('meta')
    for meta in metas:
        if meta.get('property') == name:
            return meta.get('content')
    return ''

def get_html(url, headers):
    r = requests.get(url, headers=headers)
    return r.text


def get_text(node):
    if node:
        return node.get_text().strip()
    return ''


def parse_product(filename):
    soup = BeautifulSoup(open(filename, 'r'), 'lxml')

    link = get_meta(soup, 'og:url')
    uid = _id = link.split('/')[-1].split('.')[0]
 
    title = get_text(soup.find('h1'))
    if title == '':
        print('no title found')
        return

    breadcrumbs = soup.find_all('li', 'breadcrumbs__item')
    category = []
    for l in breadcrumbs[1:]:
        category.append(get_text(l))
    if len(category) < 3:
        print('no category')
        return
    category.pop()

    price = get_text(soup.find('div', 'current-price'))

    brand = ''
    manufacturer = ''
    description = []
    table = soup.find_all('ul', 'prcard__feat-list')
    if len(table):
        rows = table[-1].find_all('li')
        for row in rows:
            td = row.find_all(True)
            label = td[0].get_text().strip().lower()
            value = td[1].get_text().strip()
            description.append(label + ' ' + value)
            if label == u'артикул:':
                uid = value
            if label.find(u'бренд:') > -1:
                brand = value
            if label.find(u'производитель:') > -1:
                manufacturer = value
                

    img = get_meta(soup, 'og:image')
    img_src = 'result/img/' + _id + '.jpeg'
    
    if img and not isfile(img_src):
        try:
            im = Image.open(requests.get(img, stream=True).raw)
            with open(img_src, 'w') as f:
                im.save(f)
        except:
            img_src = ''
            print('Failed to load img ' + ORIGIN + img)

    text_el = soup.find('div', 'prcard__desc-wrapper')
    text = ''
    if text_el:
        text = text_el.get_text().strip()
        
    return {
        'id': uid.encode('utf-8'),
        'title': title.encode('utf-8'),
        'category': category.pop(0).encode('utf-8'),
        'subcategory': ';'.join(category).encode('utf-8'),
        'price': price.encode('utf-8'),
        'brand': brand.encode('utf-8'),
        'manufacturer': manufacturer.encode('utf-8'),
        'code': ''.encode('utf-8'),
        'description': ';'.join(description).encode('utf-8'),
        'text': text.encode('utf-8'),
        'img_src': img_src.encode('utf-8'),
        'source': link.encode('utf-8')
    } 


def process(file):
    result = parse_product(join(BASE, file))
    
    if result:
        try:
            writer.writerow(result)
            print(file + ' parsed!')
        except Exception:
            print('Exception!')

def main():
    files = [f for f in listdir(BASE) if isfile(join(BASE, f))]
    pool = Pool(processes=2)
    pool.map(process, files)
    

if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
import csv
import requests
from bs4 import BeautifulSoup
from random import choice
from multiprocessing import Pool
from PIL import Image
from os import listdir
from os.path import isfile, join

ORIGIN = 'https://www.perekrestok.ru'
useragents = open('../useragents.txt').read().split('\n')

BASE = 'raw/products'

csvfile = open('result/data.csv', 'w')
fieldnames = ['id', 'title', 'category', 'subcategory', 'brand', 'manufacturer', 'price', 'price_old','code', 'description', 'text', 'img_src', 'source']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|', quotechar='~')
writer.writeheader()

def get_html(url, headers):
    r = requests.get(url, headers=headers)
    return r.text


def get_text(node):
    if node:
        return node.get_text().strip()
    return ''


def parse_product(product, source):
    name = product.split('/')[-1].strip()
    
    soup = BeautifulSoup(open('raw/products/' + name, 'r'), 'lxml')
    
    title = get_text(soup.find('h1', 'xf-product-card__title'))
    if title == '':
        print('no title found')
        return
    
    
    category = soup.find_all('a', 'xf-breadcrumbs__link')
    if len(category) < 3:
        print('no category found')
        return
        
    subcategory = [get_text(f) for f in category[2:]]
    category = subcategory.pop(0)
    subcategory = ';'.join(subcategory)
    
    price = get_text(soup.find('div', 'xf-product-cost__current'))
    price_old = get_text(soup.find('div', 'xf-product-cost__prev'))
    
    _id = name
    uid = ''
    _uid = soup.find('div', 'xf-product-card__rating-vendor')
    if _uid:
        uid = get_text(_uid.find('span', 'muted')).replace(u'Артикул', '').strip()
        _id = uid
        
    _info = soup.find('div', 'xf-product-general__info')
    text = get_text(_info.find('p', 'xf-product-info__paragh'))
    
    brand = ''
    manufacturer = ''
    description = []
    rows = soup.find_all('tr', 'xf-product-table__row')
    if len(rows):
        for row in rows:
            td = row.find_all(True)
            label = td[0].get_text().strip().lower()
            value = td[1].get_text().strip()
            description.append(label + ' ' + value)
            if label.find(u'бренд') > -1:
                brand = value
            if label.find(u'производитель') > -1:
                manufacturer = value
    description = ';'.join(description)  
        
    img = soup.find('img', 'xf-product-gallery__fullsize-img')
    img_src = 'result/img/' + _id + '.jpeg'
    
    if img and not isfile(img_src):
        try:
            im = Image.open(requests.get(ORIGIN + img.get('src'), stream=True).raw)
            with open(img_src, 'w') as f:
                im.save(f)
        except:
            img_src = ''
            print('Failed to load img ' + ORIGIN + img.get('src'))    
        
    return {
        'id': uid.encode('utf-8'),
        'title': title.encode('utf-8'),
        'category': category.encode('utf-8'),
        'subcategory': subcategory.encode('utf-8'),
        'brand': brand.encode('utf-8'),
        'manufacturer': manufacturer.encode('utf-8'),
        'price': price.encode('utf-8'),
        'price_old': price_old.encode('utf-8'),
        'code': ''.encode('utf-8'),
        'description': description.encode('utf-8'),
        'text': text.encode('utf-8'),
        'img_src': img_src,
        'source': (ORIGIN + source).encode('utf-8')
    }   


def process(product):
    name = product.split('/')[-1].strip()
    result = parse_product(join(BASE, name), product)
    
    if result:
        try:
            writer.writerow(result)
        except Exception:
            print('Exception!')


def main():
    products = open('raw/products.txt').read().split('\n')
    
    pool = Pool(20)
    pool.map(process, products)


if __name__ == '__main__':
    main()

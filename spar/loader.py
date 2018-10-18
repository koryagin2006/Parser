import codecs, csv
import requests
from bs4 import BeautifulSoup
from random import choice
import time
from os import listdir
from os.path import isfile, join
from selenium import webdriver
from multiprocessing import Pool
import json

BASE = 'raw/products'
useragents = open('../useragents.txt').read().split('\n')

csvfile = open('result/data.csv', 'w')
fieldnames = ['id', 'title', 'category', 'subcategory', 'price', 'brand', 'manufacturer', 'code', 'description', 'text', 'img_src', 'source']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()

products = json.load(open('raw/products.json', 'r'))
categories = json.load(open('raw/categories.json', 'r'))

category_map = {}
for cat in categories:
    category_map[cat['id']] = cat


def read_category(cid):
    leaf = category_map[cid]
    tree = [leaf['name']]
    while True:
        if leaf['parent_section_id'] == 0:
            break
            
        leaf = category_map[leaf['parent_section_id']]
        tree.insert(0, leaf['name'])
        
    return tree    


def get_html(url, headers):
    try:
	    r = requests.get(url, headers=headers)
	    return r.text
    except:
	    return ''


def load_product(product):
    pid = str(product['product_id'])
    print('Loading... ' + pid)
    info = get_html('https://api.my-spar.ru/products/' + pid, {'User-Agent': choice(useragents)})
    if info != 'null':
        with open('raw/products/' + pid + '.json', 'w') as f:
            f.write(info.encode('utf-8'))
            f.close()


def get_value(info, key, defaults):
    try:
        return info[key]
    except:
        return defaults


def parse_product(product):
    uid = product['product_id']
    pid = str(uid)
    
    info_file = 'raw/products/' + pid + '.json'
    if not isfile(info_file):
        print('No info file found: ' + pid)
        return
        
    source = 'https://api.my-spar.ru/products/' + pid
    f = open(info_file, 'r')
    try:
        info = json.load(f)
    except:
        info = product
        
    subcategory = read_category(info['parent_section_id'])
    category = subcategory.pop(0)
    description = []
    if len(get_value(info, 'attributes', [])) > 0:
        description = [(f['name'] + ' ' + f['value']) for f in info['attributes']]
    
    img_src = ''
    try:
        if info['images'] and info['images']['full'] and len(info['images']['full']):
            img_src = info['images']['full'][0]
    except:
        img_src = ''     
    
    return {
        'id': uid,
        'title': get_value(info, 'product_name', '').encode('utf-8'),
        'category': category.encode('utf-8'),
        'subcategory': ';'.join(subcategory).encode('utf-8'),
        'price': get_value(info, 'price', {'base_price': 0})['base_price'],
        'brand': get_value(info, 'brand_id', 0),
        'manufacturer': '',
        'code': '',
        'description': ';'.join(description).encode('utf-8'),
        'text': '',
        'img_src': img_src,
        'source': source.encode('utf-8')
    }


def process(product):
    result = parse_product(product)
    
    if result:
        try:
            writer.writerow(result)
        except Exception:
            print('Exception!')


def main():
    pool = Pool(processes=1)
    pool.map(process, products)
    print(len(products))
        
if __name__ == '__main__':
    main()

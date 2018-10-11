from os import listdir
from os.path import isfile, join
from bs4 import BeautifulSoup
import csv
from PIL import Image
import requests
from multiprocessing import Pool

HOST = 'https://www.auchan.ru/'
BASE = 'raw/products'

csvfile = open('result/data_common.csv', 'w', newline='')
fieldnames = ['id', 'title', 'category', 'subcategory', 'price', 'brand', 'manufacturer', 'code', 'description', 'text', 'img_src', 'source']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
writer.writeheader()


def get_meta(soup, name):
    metas = soup.find_all('meta')
    for meta in metas:
        if meta.get('property') == name:
            return meta.get('content')
    return ''


def parse(filename):
    soup = BeautifulSoup(open(filename, 'r', encoding='utf-8'), 'lxml')

    link = get_meta(soup, 'og:url')
    uid = _id = link.split('/')[-1].split('.')[0]
 
    title = soup.find('h1')
    if not title:
        return
    title = title.get_text().strip()

    breadcrumbs = soup.find_all('li', 'breadcrumbs__item')
    category = []
    for l in breadcrumbs[1:]:
        category.append(l.get_text().strip())
    if len(category) < 3:
        return
    category.pop()

    price = ''
    price_el = soup.find('div', 'current-price')
    if price_el:
        price = price_el.get_text().strip()

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
            if label == 'артикул:':
                uid = value
            if label.find('бренд:') > -1:
                brand = value
            if label.find('производитель:') > -1:
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
            print('Failed to load img ' + HOST + img)

    text_el = soup.find('div', 'prcard__desc-wrapper')
    text = ''
    if text_el:
        text = text_el.get_text().strip()

    return {
        'id': uid,
        'title': title,
        'category': category.pop(0),
        'subcategory': ';'.join(category),
        'price': price,
        'brand': brand,
        'manufacturer': manufacturer,
        'code': '',
        'description': ';'.join(description),
        'text': text,
        'img_src': img_src,
        'source': link
    }


def process(file):
    print(file)
    result = parse(join(BASE, file))
    if result:
        try:
            writer.writerow(result)
        except Exception:
            print('Exception!')

def main():
    files = [f for f in listdir(BASE) if isfile(join(BASE, f))]
    pool = Pool(processes=20)
    pool.map(process, files)

    """accumulator = []

    processes = [
        Process(target=process, args=(files[0:10], accumulator)),
        Process(target=process, args=(files[10:20], accumulator))
    ]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
    
    print(accumulator)"""
    #for row in accumulator:
    #    writer.writerow(row)
    

if __name__ == '__main__':
    main()

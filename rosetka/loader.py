# encoding=utf8  
import sys
import codecs, csv
import requests
from bs4 import BeautifulSoup
from random import choice
import time
from os import rename, listdir, getcwd
from os.path import isfile, join
from selenium import webdriver
from PIL import Image
from multiprocessing import Pool
import re
import json

reload(sys)
sys.setdefaultencoding('utf8')

BASE = 'raw/products'
useragents = open('../useragents.txt').read().split('\n')

#csvfile = codecs.open('result/data-2.csv', 'w', encoding='utf-8')
#fieldnames = ['title', 'category', 'subcategory', 'price', 'code', 'text', 'img_src', 'source']
#writer = csv.writer(csvfile, delimiter='|', quotechar='~')#, fieldnames=fieldnames
#writer.writerow(fieldnames)
#writer.writeheader()


def get_html(url, headers):
    try:
	    r = requests.get(url, headers=headers)
	    return r.text
    except:
	    return ''


def get_runtime_html(url, headers):
    print(url)
    options = webdriver.ChromeOptions();
    #options.add_argument('headless');
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(2)
    source_code = driver.execute_script("return window.document.documentElement.outerHTML")
    driver.quit()
    return source_code


def get_meta(soup, name):
    metas = soup.find_all('meta')
    for meta in metas:
        if meta.get('property') == name:
            return meta.get('content')
    return ''

def load_product(url):
    f = join(BASE, url.replace('/', '___') + '.html')
    if(isfile(f)):
        return
        
    info = get_html(url, {'User-Agent': choice(useragents)})
    if len(info) > 0:
        with open('raw/products/' + url.replace('/', '___') + '.html', 'w') as f:
            f.write(info.encode('utf-8'))
            f.close()
            
    else:
        print('Failed: ' + url)


def get_value(info, key, defaults):
    try:
        return info[key]
    except:
        return defaults


def get_text(node):
    try:
        return node.get_text().strip()
    except:
        return ''


def parse_product(filename):
    #html = get_runtime_html('file:' + getcwd() + '/' + filename)

    soup = BeautifulSoup(open(filename, 'r'), 'lxml')

    link = get_meta(soup, 'og:url')
    uid = _id = link.split('/')[-1].split('.')[0]
 
    title = get_text(soup.find('h1'))
    if not title or title == '':
        print('no title found')
        return

    try:
        code = str(re.search(r'\((\d+)\)', title).group(1)).strip()
    except:
        print('No code found')
        return

    if not re.match(r'\d+$', code):
        return

    breadcrumbs = soup.find_all('li', 'breadcrumbs-i')
    category = []
    for l in breadcrumbs[1:]:
        category.append(get_text(l))
    if len(category) < 3:
        print('no category')
        return

    price = get_text(soup.find('meta', itemprop='price'))

    brand = ''
    manufacturer = ''
    description = []
    text = get_text(soup.find('div', 'text-description-content'))
    img_src = ''
    """table = soup.find('table', 'chars-t')
    if len(table):
        rows = table.find_all('tr')
        for row in rows:
            td = row.find_all('td', 'chars-t-cell')
            label = get_text(td[0]).lower()
            value = get_text(td[1])
            description.append(label + ': ' + value)
    """
            
    """
    img = get_meta(soup, 'og:image')
    img_src = ''
    
    if img and not isfile('result/img/' + _id + '.jpg'):
        try:
            img_src = 'result/img/' + _id + '.jpg'
            im = Image.open(requests.get(img, stream=True).raw)
            with open(img_src, 'w') as f:
                im.save(f)
        except:
            img_src = ''
            print('Failed to load img: ' + img)
    """    
    
    return [
        title,
        category.pop(0),
        ';'.join(category),
        price,
        code,
        text,
        img_src,
        link
    ]
    
    """return {
        'title': title.encode('utf-8'),
        'category': category.pop(0).encode('utf-8'),
        'subcategory': ';'.join(category).encode('utf-8'),
        'price': price.encode('utf-8'),
        'code': code.encode('utf-8'),
        'text': text.encode('utf-8'),
        'img_src': '',
        'source': link.encode('utf-8')
    }"""


def read_cat(catUrl):
    print(catUrl)
    html = get_html(catUrl, {'User-Agent': choice(useragents)})
    soup = BeautifulSoup(html, 'lxml')
    print('html = ' + html)
    total_pages = 1
    nav = soup.find('nav', 'paginator-catalog')
    if nav:
        pages = nav.find_all('a', 'paginator-catalog-l-link')
        if len(pages) > 1:
            total_pages = int(get_text(pages[-1]))
    
    links = set(read_page(html))
    print('Pages found: ' + str(total_pages))
    
    """for page in range(2, total_pages + 1):
        link = get_page_link(catUrl, page)
        print('Parsing: ' + link)
        links.update(read_page(get_html(link, {'User-Agent': choice(useragents)})))
        print('Parsed: ' + link + '!')
    """    
    return links    
             
    
def get_page_link(base, page):
    parts = base.split('/')
    paging = 'page=' + str(page)
    if parts[-1].find('=') > -1:
        parts.append(paging)
    else:
        parts[-2] = parts[-2] + ';' + paging
        
    return '/'.join(parts)
    
    
def read_page(html):
    soup = BeautifulSoup(html, 'lxml')
    return map(lambda d: d.find('a').get('href'), soup.find_all('div', 'g-i-tile-i-title'))


def process_category(catUrl):
    if len(catUrl) > 10:
        links = read_cat(catUrl)
        with open('raw/pages/' + catUrl.replace('/', '___'), 'w') as result:
            result.write('\n'.join(set(links)))
            result.close()


def load_products(source):
    return open(source).read().split('\n')


def process(product):
    result = parse_product(product)
    
    if result:
        #try:
            writer.writerow(result)
        #except Exception:
        #    print('Exception!')


def main():
    #files = [(BASE + '/' + f) for f in listdir(BASE) if isfile(join(BASE, f))]
    #pool = Pool(processes=40)
    #pool.map(process, files)
    
    #process(files[0])
    #products = open('raw/products.txt', 'r').read().split('\n')
    #load_product(products[0])
    #pool = Pool(processes=40)
    #pool.map(load_product, products)

    cats = open('raw/cat.txt').read().split('\n')
    process_category('https://rozetka.com.ua/vesy/c4625292/')
    #pool = Pool(processes=20)
    #pool.map(process_category, cats)
    
        
if __name__ == '__main__':
    main()

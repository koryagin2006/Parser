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

csvfile = codecs.open('result/data.csv', 'w', encoding='utf-8')
fieldnames = ['title', 'category', 'code', 'text', 'source']
writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='|', quotechar='~')
#writer.writerow(fieldnames)
writer.writeheader()


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
    print('Loading '+url)    
    info = get_html('https://roskachestvo.gov.ru' + url, {'User-Agent': choice(useragents)})
    if len(info) > 0:
        with codecs.open('raw/products/' + url.replace('/', '___') + '.html', 'w', encoding='utf-8') as f:
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
    soup = BeautifulSoup(open(filename, 'r'), 'lxml')

    link = get_meta(soup, 'og:url')
    uid = _id = link.split('/')[-1]
 
    title = get_text(soup.find('h1', 'page-title'))
    if len(title.encode('utf-8')) < 3:
        print('no title found')
        return

    breadcrumbs = soup.find('div', 'breadCrumbs').find_all('a')
    category = get_text(breadcrumbs[-1])

    if len(category.encode('utf-8')) < 3:
      print('no category found!')
      return

    price = get_text(soup.find('meta', itemprop='price'))

    code = ''
    brand = ''
    manufacturer = ''
    description = []
    text = '' #get_text(soup.find('div', 'text-description-content'))
    img_src = ''
    rows = soup.find_all('div', 'product-list__item__category-title')
    rows = filter(lambda x: x.get('class')[-1].find('product-list__item__category-title--hide') == -1, rows)
    for row in rows:
      text = get_text(row)
      if len(text) > 0:
        description.append(text)
        if text.find(u'Штриховой код:') > -1:
          code = text.replace(u'Штриховой код:', '').strip()
   
    if not re.match(r'\d+', code):
        print('No code found')
        return
  
    """img = get_meta(soup, 'og:image')
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
    
    return {
        'title': title.encode('utf-8'),
        'category': category.encode('utf-8'),
        'code': code.encode('utf-8'),
        'text': ';'.join(description).encode('utf-8'),
        'source': link.encode('utf-8')
    }


def read_cat(catUrl):
    print(catUrl)
    html = get_html(catUrl, {'User-Agent': choice(useragents)})
    soup = BeautifulSoup(html, 'lxml')
    
    links = set(read_page(html))
    return links    
    
    
def read_page(html):
    soup = BeautifulSoup(html, 'lxml')
    return map(lambda a: a.get('href'), soup.find_all('a', 'product-list__item__title'))


def process_category(catUrl):
    if len(catUrl) > 10:
        links = read_cat(catUrl)
        with open('raw/pages/' + catUrl.replace('/', '___'), 'w') as result:
            result.write('\n'.join(set(links)))
            result.close()


def load_products(source):
    return open(source, 'r').read().split('\n')


def process(product):
    result = parse_product(product)
    
    if result:
        #try:
            writer.writerow(result)
        #except Exception:
        #    print('Exception!')


def main():
    files = [(BASE + '/' + f) for f in listdir(BASE) if isfile(join(BASE, f))]
    pool = Pool(processes=40)
    pool.map(process, files)
    
    #process(files[0])
    #products = load_products('raw/products.txt')
    #pool = Pool(processes=10)
    #pool.map(load_product, products)

    """links = set()
    cats = open('raw/category.txt').read().split('\n')
    for cat in cats:
      links.update(read_cat(cat))
    
    with codecs.open('raw/products.txt', 'w', encoding='utf-8') as result:
      result.write('\n'.join(links))
      result.close()"""
            
    #pool = Pool(processes=20)
    #pool.map(process_category, cats)
    
        
if __name__ == '__main__':
    main()

import codecs, csv
import requests
from bs4 import BeautifulSoup
from random import choice
import time
from os import listdir
from os.path import isfile, join
from multiprocessing import Pool

useragents = open('../useragents.txt').read().split('\n')

def get_html(url, headers):
    try:
	r = requests.get(url, headers=headers)
	return r.text
    except:
	return ''
    

def parse_sitemap(src):
    s = BeautifulSoup(open(src, 'r'), 'lxml')
    items = s.find_all('loc')
    return list(map(lambda item: item.get_text(), items))


def load_products(sitemap):
    links = parse_sitemap(sitemap)
    for url in links:
        html = get_html(url, {'User-Agent': choice(useragents)})
	if html == '':
	    print('Failed to load ' + url)
	    return
        with open('raw/products/' + url.split('/').pop(), 'w') as file:
            file.write(html.encode('utf-8'))
            file.close()


def parse_root_sitemap():
    sitemaps = parse_sitemap('sitemap_index.xml')
    for url in sitemaps:
        html = get_html(url, {'User-Agent': choice(useragents)})
        with open('raw/' + url.split('/').pop(), 'w') as file:
            file.write(html.encode('utf-8'))
            file.close()


def main():
    BASE = 'raw';

    parse_root_sitemap()

    files = [BASE + '/' + f for f in listdir(BASE) if isfile(join(BASE, f))]
    pool = Pool(processes=40)
    pool.map(load_products, files)
    
        
if __name__ == '__main__':
    main()

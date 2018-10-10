import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from random import choice
import time

useragents = open('../useragents.txt').read().split('\n')

def get_html(url, headers):
    r = requests.get(url, headers=headers)
    return r.text


def get_links(html):
    soup = BeautifulSoup(html, 'lxml')
    links = soup.find_all('a', 'xf-product-title__link')
    hrefs = set()
    if len(links) == 0:
	return res

    for link in links:
	hrefs.add(link.get('href'))

    return hrefs


def parse_cat(cat, accumulator):
    cat_name = cat.split('/')[-1]
    for i in range(1, 10000):
	page = str(i)
	url = cat + '?page=' + page
	html = get_html(url, {'User-Agent': choice(useragents)})

	links = get_links(html)
	print(url+' ' +str(len(links)))
	if len(links.difference(accumulator)) == 0:
	    print(cat_name + ' parsed! Total pages: ' + page)
	    return

	for link in links:
	    accumulator.add(link)


def main():
    cats = open('category.txt').read().split('\n')

    links = set()

    for cat in cats:
	if len(cat.strip()) > 0:
            print('parsing ' + cat)
	    parse_cat(cat, links)

    file = open('raw/products.txt', 'w');
    file.write('\n'.join(links))
    file.close()


if __name__ == '__main__':
    main()

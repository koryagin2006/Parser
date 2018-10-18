import codecs, csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from random import choice


def get_html(url, headers):
    r = requests.get(url, headers=headers)
    return r.text


def get_links(html, result):
    soup = BeautifulSoup(html, 'lxml')
    links = soup.find_all('a', 'product__link')
    for link in links:
        result.add(link.get('href'))


def main():
    BASE_HREF = 'https://magnitcosmetic.ru'
    useragents = open('../useragents.txt').read().split('\n')
    
    product_links = set()
    
    for page in range(1, 884):
        with open('raw/pages/page-' + str(page) + '.html', 'r', encoding='utf-8') as file:
            html = file.read()
            get_links(html, product_links)
            file.close()

    for link in product_links:
        url = BASE_HREF + link;
        html = get_html(url, {'User-Agent': choice(useragents)})
        filename = link.replace('/', '_')
        with open('raw/products/' + filename + '.html', 'w', encoding='utf-8') as file:
            file.write(html)
            file.close()


if __name__ == '__main__':
    main()

import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from random import choice
import time


def get_html(url, headers):
    r = requests.get(url, headers=headers)
    return r.text


def get_links(html):
    soup = BeautofulSoup(html, 'lxml')


def main():
    BASE_HREF = 'https://magnitcosmetic.ru/catalog/?PAGEN_1='
    useragents = open('../useragents.txt').readlines()
    cats = open('category.txt').readlines()

    print(cats)

    """for page in range(1, 5):
        url = BASE_HREF + str(page)
        #time.sleep(choice([1, 2]))
        print(url)
        html = get_html(url, {'User-Agent': choice(useragents)})
        with open('raw/pages/page-' + str(page) + '.html', 'w', encoding='utf-8') as file:
            file.write(html)
            file.close()"""


if __name__ == '__main__':
    main()

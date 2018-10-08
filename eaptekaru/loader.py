import codecs, csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from random import choice
import time
from selenium import webdriver


def get_html(url):
    options = webdriver.ChromeOptions();
    #options.add_argument('headless');

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(2)
    source_code = driver.execute_script("return window.document.documentElement.innerHTML")
    driver.quit()
    return source_code


def get_links(html):
    soup = BeautofulSoup(html, 'lxml')


def main():
    start = datetime.now()

    cats = [
        {'path': 'drugs', 'size': 498},
        {'path': 'beauty', 'size': 1064},
        {'path': 'bytovaya_khimiya', 'size': 61},
        {'path': 'gigiena', 'size': 135},
        {'path': 'linzy', 'size': 180},
        {'path': 'mother', 'size': 145},
        {'path': 'medical', 'size': 210},
        {'path': 'ortopedicheskie_izdeliya', 'size': 49},
        {'path': 'intimnye_tovary', 'size': 13}
    ]

    BASE_HREF = 'https://www.eapteka.ru/goods/'
    useragents = open('../useragents.txt').read().split('\n')


    for page in range(192, 1064):
        spage = str(page)
        url = BASE_HREF + 'beauty/?PAGEN_1=' + spage;
        html = get_html(url)
        with open('raw/pages/beauty-' + spage + '.html', 'w', encoding='utf-8') as file:
            file.write(html)
            file.close()

"""
    for cat in cats:
        for page in range(cat['size']):
            spage = str(page)
            url = BASE_HREF + cat['path'] + '/?PAGEN_1=' + spage;
            html = get_html(url)
            with open('raw/pages/' + cat['path'] + '-' + spage + '.html', 'w', encoding='utf-8') as file:
                file.write(html)
                file.close()

"""

if __name__ == '__main__':
    main()

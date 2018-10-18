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
from pyvirtualdisplay import Display
from PIL import Image
from multiprocessing import Pool
import re
import json


reload(sys)
sys.setdefaultencoding('utf8')


def get_html(url):
    print('Parse: ' + url)
    options = webdriver.ChromeOptions();
    #options.add_argument('--headless');
    #options.add_argument('--disable-gpu')
    
    display = Display(visible=0, size=(1920, 1080))
    display.start()
    
    try:
      driver = webdriver.Chrome(options=options)
      driver.get(url)
    except:
      time.sleep(2)
      driver.get(url)
    
    time.sleep(choice([2, 3, 4]))
    source_code = driver.execute_script("return window.document.documentElement.innerHTML")
    print('Done: ' + url)
    
    driver.quit()
    display.stop()
    
    return source_code


def get_links(html):
    soup = BeautofulSoup(html, 'lxml')


def process_page(info):
  cat = info['cat']
  page = info['page']
  url = info['url']
  html = get_html(url)
  with codecs.open('raw/pages/' + cat['path'] + '-' + page + '.html', 'w', encoding='utf-8') as file:
      try:
        file.write(html)
      except:
        print('Error : ' + url)
      file.close()

def main():
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


    """for page in range(192, 1064):
        spage = str(page)
        url = BASE_HREF + 'beauty/?PAGEN_1=' + spage;
        html = get_html(url)
        with open('raw/pages/beauty-' + spage + '.html', 'w', encoding='utf-8') as file:
            file.write(html)
            file.close()"""

    data = []
    for cat in cats:
        for page in range(1, cat['size'] + 1):
            spage = str(page)
            url = BASE_HREF + cat['path'] + '/?PAGEN_1=' + spage;
            process_page({
              'cat': cat,
              'page': spage,
              'url': url
            })
            
            """data.append({
              'cat': cat,
              'page': spage,
              'url': url
            })"""
    
    #pool = Pool(processes=5)
    #pool.map(process_page, data)          


if __name__ == '__main__':
    main()

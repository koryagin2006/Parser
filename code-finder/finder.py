# -*- coding: utf-8 -*-  
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


def load_rategoods(code):
  url = 'https://ratengoods.com/ajax_search_product/'
  params = {
      'query': code,
      'lang': 'ru',
      'show_price': 'true'
  }
  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
             'X-Requested-With': 'XMLHttpRequest',
             'Host': 'ratengoods.com',
             'Referer': 'https://ratengoods.com'}

  response = requests.get(url, params=params, headers=headers)
  try:
    text = response.text
  except:
    text = ''
    
  try:   
    data = json.loads(text)['products']
  except:
    data = []
  
  if len(data) == 0:
    print('No products found! Code: ' + str(code))
    return
  
  data = data[0]['properties']
  data['code'] = code
  data['query'] = {
    'url': url,
    'params': params
  };
  
  return data
  
  
def main():
    data = []

    reader = csv.reader(open('raw/barcodes_with_segments.csv', 'r'))
    for row in reader:
        if row[0] != 'ШТРИХКОД':
          item = load_rategoods(row[0])
          if item:
            data.append(item)
            print(item)
    
    writer = codecs.open('result/barcodes_with_segments.json', 'w', encoding='utf-8')
    writer.write(json.dumps(data, indent=2))
    writer.close()   
        
if __name__ == '__main__':
    main()  
  
    

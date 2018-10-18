import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from random import choice
from multiprocessing import Pool
from os import listdir
from os.path import isfile, join


ORIGIN = 'https://www.perekrestok.ru'
useragents = open('../useragents.txt').read().split('\n')

BASE = 'raw/products'


def main():
    files = [f for f in listdir(BASE) if isfile(join(BASE, f))]
    for f in files:
        with open(join(BASE, f), 'r') as fp:
            if fp.read().find('Service Unavailable') > -1:
                print(join(BASE, f) + ' broken!')
            fp.close()
    

if __name__ == '__main__':
    main()    

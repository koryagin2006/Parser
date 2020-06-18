from pathlib import Path
import codecs
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time
from datetime import datetime

host = 'https://stolichki.ru'
result_path = 'result/%s' % datetime.today().date()

Path(result_path).mkdir(parents=True, exist_ok=True)

def parse_product(id, city_id, city_title):
    html = requests.get('%s/drugs/%d' % (host, id), cookies={'cityId': city_id})
    page = BeautifulSoup(html.text, features='html.parser')
    product = page.find('div', {'class': 'product-info'})

    if product == None:
        return

    title = product.find('h1')
    if title == None:
        return

    price_block = product.find('div', {'class': 'part-price'})

    if price_block == None:
        return

    price = price_block.find('p', attrs={'itemprop' : 'lowPrice'})
    price_old = price_block.find('b', attrs={'itemprop' : 'lowPrice'})

    price = price.text.strip() if price != None else 0
    price_old = price_old.text.strip() if price_old != None else 0

    res = pd.DataFrame()
    return res.append(pd.DataFrame([[city_title, title.text, price_old != 0, price, price_old]], columns = ['city', 'title', 'sale', 'price', 'price_old']), ignore_index=True)

cities = {
   "1": "Москва",
   #"6": "Дмитров",
   #"19": "Щелково",
   #"25": "Луховицы",
   #"26": "Ногинск",
   "27": "Люберцы",
   #"28": "Подольск",
   #"29": "Дзержинский",
   #"30": "Егорьевск",
   #"31": "Коломна",
   #"32": "Фрязино",
   #"33": "Орехово-Зуево",
   #"35": "Реутов",
   #"36": "Долгопрудный",
   #"38": "Одинцово",
   #"39": "Железнодорожный",
   "40": "Тула",
   #"43": "Муром",
   "44": "Балашиха",
   #"45": "Серебряные пруды",
   #"46": "Сергиев Посад",
   #"48": "Ликино-Дулево",
   #"50": "Серпухов",
   #"51": "Щёкино",
   "52": "Владимир",
   #"53": "Александров",
   #"54": "Черноголовка",
   #"55": "пос. Большевик",
   #"56": "Ковров",
   #"59": "Чехов",
   #"60": "Королёв",
   #"61": "Лобня",
   #"62": "Химки",
   "63": "Рязань",
   #"64": "Клин",
   #"65": "Кашира",
   #"66": "Ступино",
   #"67": "Пересвет",
   #"68": "Яхрома",
   #"69": "Красногорск",
   #"70": "Павловский Посад",
   #"71": "Зеленоград",
   #"75": "Раменское",
   "76": "Кострома",
   "77": "Санкт-Петербург",
   #"78": "Красногорский район",
   "79": "Мытищи",
   #"80": "Куровское",
   #"81": "Юрьев-Польский",
   #"82": "Донской",
   #"83": "Орехово-Зуевский район",
   #"84": "Пушкино",
   "85": "Иваново",
   "86": "Вязники",
   #"88": "Старая Купавна",
   "89": "Кольчугино",
   #"90": "Дубна",
   #"91": "Электросталь",
   #"92": "р.п. Лесной",
   #"93": "п. Пирогово",
   "94": "Новомосковск",
   #"96": "Сестрорецк",
   #"97": "Колпино",
   #"98": "Котельники",
   #"99": "р.п. Октябрьский",
   "100": "Ярославль",
   #"101": "Кимовск",
   #"102": "Истра",
   #"103": "Кронштадт ",
   #"104": "пос. Десёновское",
   #"105": "мкр.Град Московский",
   #"106": "Бронницы",
   #"107": "Дедовск ",
   #"108": "Гатчина",
   #"109": "Судогда ",
   #"110": "Жуковский",
   #"113": "Зарайск",
   #"114": "Озёры",
   #"115": "Домодедово",
   #"116": "Звенигород",
   #"117": "Лыткарино",
   #"118": "Солнечногорск",
   #"119": "п.Мосрентген",
   #"120": "Радужный",
   #"121": "п.Рязановское",
   #"122": "Можайск",
   "123": "Шушары",
   #"124": "Наро-Фоминск",
   "125": "Узловая"
   #"127": "Ивантеевка",
   #"128": "Тейково",
   #"129": "Шатура",
   #"130": "Малаховка",
   #"131": "Струнино",
   #"132": "Сертолово"
 }

for city_id in cities:
    result = pd.DataFrame()
    city = cities[city_id]
    start = time.time()
    for id in range(0, 38000):
        print(city, id)
        result = result.append(parse_product(id, city_id, city), ignore_index=True)
        result.to_csv('%s/%s.csv' % (result_path, city))

        time.sleep(.3)

    with open('result/time.txt', 'a') as file:
        file.write('%s crawl time %f\n' % (city, time.time() - start))
        file.close()

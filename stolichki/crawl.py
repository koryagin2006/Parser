from pathlib import Path
import codecs
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

host = 'https://stolichki.ru'

Path('raw').mkdir(parents=True, exist_ok=True)
Path('result').mkdir(parents=True, exist_ok=True)

def parse_product(id, city_id, city_title):
    html = requests.get('%s/drugs/%d' % (host, id), cookies={'cityId': city_id})
    page = BeautifulSoup(html.text, features='html.parser')
    product = page.find('div', {'class': 'product-info'})

    if product == None:
        return

    title = product.find('h1')
    if title == None:
        return

    price = product.find('div', {'class': 'part-price'})

    if price == None:
        return

    price = price.text.strip()

    res = pd.DataFrame()
    return res.append(pd.DataFrame([[city_title, title.text, price, price]], columns = ['city', 'title', 'price_min', 'price_max']), ignore_index=True)

cities = {
   #"1": "Москва",
   #"6": "Дмитров",
   #"19": "Щелково",
   #"25": "Луховицы",
   #"26": "Ногинск",
   #"27": "Люберцы",
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
   #"40": "Тула",
   #"43": "Муром",
   #"44": "Балашиха",
   #"45": "Серебряные пруды",
   #"46": "Сергиев Посад",
   #"48": "Ликино-Дулево",
   #"50": "Серпухов",
   #"51": "Щёкино",
   #"52": "Владимир",
   #"53": "Александров",
   #"54": "Черноголовка",
   #"55": "пос. Большевик",
   #"56": "Ковров",
   #"59": "Чехов",
   #"60": "Королёв",
   #"61": "Лобня",
   #"62": "Химки",
   #"63": "Рязань",
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
    for id in range(0, 38000):
        print(city, id)
        result = result.append(parse_product(id, city_id, city), ignore_index=True)
        result.to_csv('result/%s.csv' % city)

        time.sleep(.3)


"""
r = requests.get(url + '/catalog')
with codecs.open('raw/catalog.html', 'w', 'utf-8') as output_file:
    output_file.write(r.text)

catalog = BeautifulSoup(r.text, features='html.parser')
category_links = catalog.find('div', {'class': 'catalog-categories'}).find_all('a')

for link in category_links:
    print(link.get('href'))
    print(link.text)


def parse_category(category_link):
    res = pd.DataFrame()
"""

"""
prices_url = '%s/ajax/product-map?id=%d' % (host, id)

    session = requests.Session()
    session.head(prices_url)

    prices = session.get(
        url=prices_url,
        data={},
        headers={
            'Referer': url,
            'x-requested-with': 'XMLHttpRequest'
        }
    )

    json_string = json.dumps(prices.text)
    print(json_string)
"""

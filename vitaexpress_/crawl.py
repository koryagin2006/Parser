from pathlib import Path
import codecs
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import pandas as pd
import json
import time
import math
import urllib.parse

host = 'https://vitaexpress.ru'

Path('raw').mkdir(parents=True, exist_ok=True)
Path('result').mkdir(parents=True, exist_ok=True)

def parse_product(product, city_title):
    def parse_price(price):
        if price == None:
            return '0'

        price_parts = []
        for child in price.children:
            if isinstance(child, Tag):
                if 'priceSVG__num' in child.get('class'):
                    price_parts.append(price_convert_map[child.find('use').attrs['xlink:href'].split('-')[-1]])

                if 'priceSVG__separ' in child.get('class'):
                    price_parts.append('.')

        return ''.join(price_parts)

    title = product.find('span', {'itemprop': 'name'})

    print(title.text)
    if title == None:
        return

    price = product.find('span', {'class': 'priceSVG'})
    if price == None:
        return

    price_convert_map = {
        '0': '5',
        '1': '9',
        '2': '7',
        '3': '6',
        '4': '4',
        '5': '0',
        '6': '8',
        '7': '2',
        '8': '3',
        '9': '1',
    }
    price = parse_price(price)
    price_old = parse_price(product.find('span', {'class': 'priceSVG--old'}))

    print(price, price_old)

    return pd.DataFrame([[city_title, title.text, price_old != '0', price, price_old]], columns = ['city', 'title', 'sale', 'price', 'price_old'])

def parse_category(df, user_city, city, category_def):
    def grep(page_href):
        print(page_href)

        session = requests.Session()
        session.head(page_href)

        r = session.get(
            url=page_href,
            data={},
            headers={
                'Referer': page_href,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
            },
            cookies={
                'PHPSESSID': '88q1opk94tui4ql64jglpgptpm',
                'user_city': user_city,
                'list-city': '1',
                'info-sticky': '1',
                'BX_USER_ID': '18474e0c50cb5c8c84f9e1964f792606',
                'TS2fa81da0029=08988fd746ab2800c55e70f1e0c6b2aa2f1234207a694f7631cb7fb936cbaa80f44b8e5c51f081c1448206ac8e6b876e': ''
            }
        )
        catalog = BeautifulSoup(r.text, features='html.parser')

        return {
            'products': catalog.find_all('div', {'class': 'product'}),
            'last': catalog.find('a', {'class': 'js-pager-next'}) == None
        }

    max_page = math.ceil(category_def['max'] / 24)
    last_product = None

    for i in range(0, max_page):
        data = grep('%s/ajax/filter.php?sort=PROPERTY_CATALOG_SORT&direction=DESC&filters=%d&brands=&props=&gamma=&PAGEN_2=%d&PAGEN_1=%d&subsect=&sect=&min=0&max=%d&menuSection=&gammaShow=N&brandCode=&landingCode=&tagCode=' % (host, category_def['id'], i + 1, i, category_def['max']))

        last_product_id = data['products'][-1].attrs['data-id']
        if last_product == last_product_id:
            break

        last_product = last_product_id
        for product in data['products']:
            df = df.append(parse_product(product, city), ignore_index=True)

        df.to_csv('result/%s.csv' % city)
        time.sleep(.5)

    return df

"""
for city_id in cities:
    result = pd.DataFrame()
    city = cities[city_id]
    for id in range(0, 38000):
        print(city, id)
        result = result.append(parse_product(id, city_id, city), ignore_index=True)
        result.to_csv('result/%s.csv' % city)

        time.sleep(.5)
"""

"""
categories = [
    '/lekarstva-i-bady/vitaminy-i-mikroelementy/,/lekarstva-i-bady/bio_add/,/lekarstva-i-bady/lekarstva-ot-prostudy/,/lekarstva-i-bady/obezbolivayushchie/,/lekarstva-i-bady/zheludochno-kishechnye-preparaty/,/lekarstva-i-bady/lekarstva-dlya-lecheniya-pochek/,/lekarstva-i-bady/sredstva-ot-allergii/,/lekarstva-i-bady/zhenskoe-zdorove/,/lekarstva-i-bady/korrektsiya-figury/,/lekarstva-i-bady/muzhskoe-zdorove/,/lekarstva-i-bady/zdorovyy-obraz-zhizni/,/lekarstva-i-bady/lekarstva-pri-kozhnykh-zabolevaniyakh/,/lekarstva-i-bady/zdorovye-veny-gemorroy/,/lekarstva-i-bady/zdorovoe-serdtse-i-sosudy/,/lekarstva-i-bady/lekarstva-pri-nevrologicheskikh-rasstroystvakh/,/lekarstva-i-bady/lekarstva-dlya-lecheniya-sustavov/,/lekarstva-i-bady/lekarstva-pri-gormonalnykh-narusheniyakh/,/lekarstva-i-bady/lekarstva-i-bady-dlya-glaz/,/lekarstva-i-bady/lekarstvennye-travy/,/lekarstva-i-bady/vaktsiny-syvorotki/,/lekarstva-i-bady/antibiotiki/,/lekarstva-i-bady/protivogribkovye-sredstva/,/lekarstva-i-bady/lekarstva-pri-infektsionnykh-zabolevaniyakh/,/lekarstva-i-bady/preparaty-dlya-sistemnogo-vozdeystviya/,/lekarstva-i-bady/okazanie-pervoy-pomoshchi/,/lekarstva-i-bady/raznoe/',
    '/dlya-krasoty-i-gigieny/ukhod-za-litsom/,/dlya-krasoty-i-gigieny/ukhod-za-telom/,/dlya-krasoty-i-gigieny/ukhod-za-volosami/,/dlya-krasoty-i-gigieny/sredstva-dlya-muzhchin/,/dlya-krasoty-i-gigieny/podarochnye-nabory-suveniry/,/dlya-krasoty-i-gigieny/solntsezashchitnye-sredstva/,/dlya-krasoty-i-gigieny/rasprodazha/,/dlya-krasoty-i-gigieny/brand/600/,/dlya-krasoty-i-gigieny/brand/6/,/dlya-krasoty-i-gigieny/brand/28/,/dlya-krasoty-i-gigieny/brand/723/,/dlya-krasoty-i-gigieny/brand/201/,/dlya-krasoty-i-gigieny/brand/179/,/dlya-krasoty-i-gigieny/brand/350/,/dlya-krasoty-i-gigieny/brand/18/,/dlya-krasoty-i-gigieny/brand/222/,/dlya-krasoty-i-gigieny/brand/94/,/dlya-krasoty-i-gigieny/brand/181/,/dlya-krasoty-i-gigieny/brand/1226/,/dlya-krasoty-i-gigieny/brand/121/,/dlya-krasoty-i-gigieny/brand/7/',
    '/beauty_health/medic_tools/,/beauty_health/landing/hygiene/,/beauty_health/landing/cosmetics/,/beauty_health/landing/intimate_health/,/beauty_health/landing/ukhod-za-bolnymi/,/beauty_health/landing/healthy_and_curative_nutrition/,/beauty_health/landing/optic/,/beauty_health/sredstva-zashchity-ot-nasekomykh/',
    '/mama-i-malysh/detskoe-pitanie/,/mama-i-malysh/detskaya-gigiena/,/mama-i-malysh/predmety-ukhoda-za-rebenkom/,/mama-i-malysh/belye-dlya-mamy/,/mama-i-malysh/dlya-kormleniya-grudyu/,/mama-i-malysh/detskaya-kosmetika/,/mama-i-malysh/kosmetika-dlya-beremennykh-i-kormyashchikh-mam/,/mama-i-malysh/pitanie-dlya-mamy/,/mama-i-malysh/tekstil/,/mama-i-malysh/igrushki/',
    '/pribory-i-apparaty/ionizatory-uvlazhniteli-obluchateli/,/pribory-i-apparaty/pribory-dlya-izmereniya-davleniya/,/pribory-i-apparaty/pribory-dlya-izmereniya-temperatury-tela/,/pribory-i-apparaty/pribory-dlya-izmereniya-urovnya-sakhara/,/pribory-i-apparaty/pribory-dlya-ingalyatsiy/,/pribory-i-apparaty/pribory-dlya-kontrolya-massy-tela/,/pribory-i-apparaty/pribory-dlya-massazha/,/pribory-i-apparaty/pribory-dlya-proslushivaniya/,/pribory-i-apparaty/for-physiotherapy/,/pribory-i-apparaty/sredstva-vizualnoy-diagnostiki-ekspress-analiz/,/pribory-i-apparaty/hygiene_of_teeth/,/pribory-i-apparaty/coagulometers/,/pribory-i-apparaty/beauty_devices/',
    '/lechebnyy-trikotazh-i-ortopediya/bandazhi-korsety-poyasa/,/lechebnyy-trikotazh-i-ortopediya/golovoderzhateli-shina-vorotnik/,/lechebnyy-trikotazh-i-ortopediya/korrektory-osanki/,/lechebnyy-trikotazh-i-ortopediya/kostyli-trosti-nakostylniki/,/lechebnyy-trikotazh-i-ortopediya/ogranichiteli-na-sustavy/,/lechebnyy-trikotazh-i-ortopediya/odezhda-dlya-fitnesa/,/lechebnyy-trikotazh-i-ortopediya/ortopedicheskie-podushki/,/lechebnyy-trikotazh-i-ortopediya/protivovarikoznyy-trikotazh/,/lechebnyy-trikotazh-i-ortopediya/stelki-polustelki-mezhpaltsevye-vkladyshi/,/lechebnyy-trikotazh-i-ortopediya/shoe/,/lechebnyy-trikotazh-i-ortopediya/belt/'
]

result = {}

for cat in categories:
    list = cat.split(',')

    for link in list:
        url = '%s/catalog%s' % (host, link)

        session = requests.Session()
        session.head(url)

        html = session.get(
            url=url,
            data={},
            headers={
                'Referer': url,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
            }
        )

        page = BeautifulSoup(html.text, features='html.parser')
        cat_id = page.find('div', {'id': 'id-cat'})

        if cat_id == None:
            print('No cat_id')
            continue

        pager = page.find('div', {'class': 'js-contentPager'})

        cat = cat_id.attrs['data-id']

        result[cat] = pager.attrs['data-max']
        print(result)

        time.sleep(3)
"""

cities = {
    'Астрахань': '%7B%22id%22%3A%2299385%22%2C%22name%22%3A%22%5Cu0410%5Cu0441%5Cu0442%5Cu0440%5Cu0430%5Cu0445%5Cu0430%5Cu043d%5Cu044c%22%7D'
}

cats = {
    '836': '4297', '3706': '6297', '804': '2135', '1121': '10419', '877': '14300', '1244': '3729', '1167': '6159', '898': '23244', '911': '25600', '1128': '6990', '1154': '19979',
    '920': '3769', '1158': '2515', '1035': '117810', '1028': '8226', '1086': '30769', '1132': '14897', '1101': '4338', '963': '229', '1172': '40500', '860': '13477', '1214': '2868', '1024': '10150', '1148': '120156', '1230': '10197', '931': '999', '2446': '8010', '2458': '5431', '2488': '5020', '2551': '4769', '2567': '8620', '2586': '3179', '3730': '1609', '3735': '1799', '1248': '418', '2863': '2699', '2879': '1749', '2888': '4939', '2944': '2099', '2947': '8639', '2951': '2519', '2977': '1919', '2983': '407', '2986': '2409', '3011': '723', '990': '4001', '996': '7049', '1001': '4800', '1002': '8340', '1005': '14309', '1011': '5820', '1012': '9059', '1013': '779', '1014': '57241', '1015': '399',
    '3715': '4297', '3718': '36518', '3719': '914', '1187': '4100', '1189': '3860', '1190': '5780', '1191': '13719', '1192': '13690', '1198': '5489', '1199': '8690', '1200': '10799', '1207': '3015', '3708': '11299', '3709': '16890'
}

for city in cities:
    result = pd.DataFrame()
    for cat_id in cats:
        result = parse_category(result, cities[city], city, {
            'id': int(cat_id),
            'max': int(cats[cat_id]),
        })


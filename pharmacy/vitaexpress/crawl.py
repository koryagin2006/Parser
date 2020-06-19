from pathlib import Path
import codecs
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
import pandas as pd
import json
import time
import math
import urllib.parse
from datetime import datetime

host = 'https://vitaexpress.ru'
result_path = 'result/%s' % datetime.today().date()

Path(result_path).mkdir(parents=True, exist_ok=True)

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
        '0': '3',
        '1': '0',
        '2': '4',
        '3': '6',
        '4': '5',
        '5': '7',
        '6': '1',
        '7': '2',
        '8': '8',
        '9': '9',
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

        if len(data['products']) == 0:
            break

        last_product_id = data['products'][-1].attrs['data-id']
        if last_product == last_product_id:
            break

        last_product = last_product_id
        for product in data['products']:
            df = df.append(parse_product(product, city), ignore_index=True)

        df.to_csv('%s/%s.csv' % (result_path, city))
        time.sleep(2)

    return df

cities = {
    #'Астрахань': '%7B%22id%22%3A%2299385%22%2C%22name%22%3A%22%5Cu0410%5Cu0441%5Cu0442%5Cu0440%5Cu0430%5Cu0445%5Cu0430%5Cu043d%5Cu044c%22%7D',
    #'Ахтубинск': '%7B%22id%22%3A%22104333%22%2C%22name%22%3A%22%5Cu0410%5Cu0445%5Cu0442%5Cu0443%5Cu0431%5Cu0438%5Cu043d%5Cu0441%5Cu043a%22%7D',
    #'Камызяк': '%7B%22id%22%3A%22102538%22%2C%22name%22%3A%22%5Cu041a%5Cu0430%5Cu043c%5Cu044b%5Cu0437%5Cu044f%5Cu043a%22%7D',
    #'Белгород': '%7B%22id%22%3A%22101980%22%2C%22name%22%3A%22%5Cu0411%5Cu0435%5Cu043b%5Cu0433%5Cu043e%5Cu0440%5Cu043e%5Cu0434%22%7D',
    #'Старый Оскол': '%7B%22id%22%3A%22101047%22%2C%22name%22%3A%22%5Cu0421%5Cu0442%5Cu0430%5Cu0440%5Cu044b%5Cu0439+%5Cu041e%5Cu0441%5Cu043a%5Cu043e%5Cu043b%22%7D',
    'Владимир': '%7B%22id%22%3A%2280950%22%2C%22name%22%3A%22%5Cu0412%5Cu043b%5Cu0430%5Cu0434%5Cu0438%5Cu043c%5Cu0438%5Cu0440%22%7D',
    'Волгоград': '%7B%22id%22%3A%2216%22%2C%22name%22%3A%22%5Cu0412%5Cu043e%5Cu043b%5Cu0433%5Cu043e%5Cu0433%5Cu0440%5Cu0430%5Cu0434%22%7D',
    'Волжский': '%7B%22id%22%3A%2259%22%2C%22name%22%3A%22%5Cu0412%5Cu043e%5Cu043b%5Cu0436%5Cu0441%5Cu043a%5Cu0438%5Cu0439%22%7D',
    'Камышин': '%7B%22id%22%3A%2256%22%2C%22name%22%3A%22%5Cu041a%5Cu0430%5Cu043c%5Cu044b%5Cu0448%5Cu0438%5Cu043d%22%7D',
    'Череповец': '%7B%22id%22%3A%22101482%22%2C%22name%22%3A%22%5Cu0427%5Cu0435%5Cu0440%5Cu0435%5Cu043f%5Cu043e%5Cu0432%5Cu0435%5Cu0446%22%7D',
    'Воронеж': '%7B%22id%22%3A%2259050%22%2C%22name%22%3A%22%5Cu0412%5Cu043e%5Cu0440%5Cu043e%5Cu043d%5Cu0435%5Cu0436%22%7D',
    'Лиски': '%7B%22id%22%3A%22101764%22%2C%22name%22%3A%22%5Cu041b%5Cu0438%5Cu0441%5Cu043a%5Cu0438%22%7D',
    'Борисоглебск': '%7B%22id%22%3A%2280802%22%2C%22name%22%3A%22%5Cu0411%5Cu043e%5Cu0440%5Cu0438%5Cu0441%5Cu043e%5Cu0433%5Cu043b%5Cu0435%5Cu0431%5Cu0441%5Cu043a%22%7D',
    'Иваново': '%7B%22id%22%3A%2272537%22%2C%22name%22%3A%22%5Cu0418%5Cu0432%5Cu0430%5Cu043d%5Cu043e%5Cu0432%5Cu043e%22%7D',
    'Калуга': '%7B%22id%22%3A%22101230%22%2C%22name%22%3A%22%5Cu041a%5Cu0430%5Cu043b%5Cu0443%5Cu0433%5Cu0430%22%7D',
    'Киров': '%7B%22id%22%3A%2299721%22%2C%22name%22%3A%22%5Cu041a%5Cu0438%5Cu0440%5Cu043e%5Cu0432%22%7D',
    'Кострома': '%7B%22id%22%3A%22100010%22%2C%22name%22%3A%22%5Cu041a%5Cu043e%5Cu0441%5Cu0442%5Cu0440%5Cu043e%5Cu043c%5Cu0430%22%7D',
    'Нерехта': '%7B%22id%22%3A%22101011%22%2C%22name%22%3A%22%5Cu041d%5Cu0435%5Cu0440%5Cu0435%5Cu0445%5Cu0442%5Cu0430%22%7D',
    'Краснодар': '%7B%22id%22%3A%2263318%22%2C%22name%22%3A%22%5Cu041a%5Cu0440%5Cu0430%5Cu0441%5Cu043d%5Cu043e%5Cu0434%5Cu0430%5Cu0440%22%7D',
    'Сочи': '%7B%22id%22%3A%22100860%22%2C%22name%22%3A%22%5Cu0421%5Cu043e%5Cu0447%5Cu0438%22%7D',
    'Новороссийск': '%7B%22id%22%3A%22101948%22%2C%22name%22%3A%22%5Cu041d%5Cu043e%5Cu0432%5Cu043e%5Cu0440%5Cu043e%5Cu0441%5Cu0441%5Cu0438%5Cu0439%5Cu0441%5Cu043a%22%7D',
    'Мурино': '%7B%22id%22%3A%2299894%22%2C%22name%22%3A%22%5Cu041c%5Cu0443%5Cu0440%5Cu0438%5Cu043d%5Cu043e+%5Cu0434%22%7D',
    'Всеволожск': '%7B%22id%22%3A%22102902%22%2C%22name%22%3A%22%5Cu0412%5Cu0441%5Cu0435%5Cu0432%5Cu043e%5Cu043b%5Cu043e%5Cu0436%5Cu0441%5Cu043a%22%7D',
    'Липецк': '%7B%22id%22%3A%2272713%22%2C%22name%22%3A%22%5Cu041b%5Cu0438%5Cu043f%5Cu0435%5Cu0446%5Cu043a%22%7D',
    'Елец': '%7B%22id%22%3A%22102696%22%2C%22name%22%3A%22%5Cu0415%5Cu043b%5Cu0435%5Cu0446%22%7D',
    'Балашиха': '%7B%22id%22%3A%22101791%22%2C%22name%22%3A%22%5Cu0411%5Cu0430%5Cu043b%5Cu0430%5Cu0448%5Cu0438%5Cu0445%5Cu0430%22%7D',
    'Нижний Новгород': '%7B%22id%22%3A%2254959%22%2C%22name%22%3A%22%5Cu041d%5Cu0438%5Cu0436%5Cu043d%5Cu0438%5Cu0439+%5Cu041d%5Cu043e%5Cu0432%5Cu0433%5Cu043e%5Cu0440%5Cu043e%5Cu0434%22%7D',
    'Дзержинск': '%7B%22id%22%3A%2257198%22%2C%22name%22%3A%22%5Cu0414%5Cu0437%5Cu0435%5Cu0440%5Cu0436%5Cu0438%5Cu043d%5Cu0441%5Cu043a%22%7D',
    'Арзамас': '%7B%22id%22%3A%2261572%22%2C%22name%22%3A%22%5Cu0410%5Cu0440%5Cu0437%5Cu0430%5Cu043c%5Cu0430%5Cu0441%22%7D',
    'Оренбург': '%7B%22id%22%3A%2272011%22%2C%22name%22%3A%22%5Cu041e%5Cu0440%5Cu0435%5Cu043d%5Cu0431%5Cu0443%5Cu0440%5Cu0433%22%7D',
    'Орск': '%7B%22id%22%3A%22100923%22%2C%22name%22%3A%22%5Cu041e%5Cu0440%5Cu0441%5Cu043a%22%7D',
    'Бузулук': '%7B%22id%22%3A%22101161%22%2C%22name%22%3A%22%5Cu0411%5Cu0443%5Cu0437%5Cu0443%5Cu043b%5Cu0443%5Cu043a%22%7D',
    'Пенза': '%7B%22id%22%3A%2212%22%2C%22name%22%3A%22%5Cu041f%5Cu0435%5Cu043d%5Cu0437%5Cu0430%22%7D',
    'Кузнецк': '%7B%22id%22%3A%2213%22%2C%22name%22%3A%22%5Cu041a%5Cu0443%5Cu0437%5Cu043d%5Cu0435%5Cu0446%5Cu043a%22%7D',
    'Заречный': '%7B%22id%22%3A%2256936%22%2C%22name%22%3A%22%5Cu0417%5Cu0430%5Cu0440%5Cu0435%5Cu0447%5Cu043d%5Cu044b%5Cu0439%22%7D',
    'Яблоновский': '%7B%22id%22%3A%2273342%22%2C%22name%22%3A%22%5Cu042f%5Cu0431%5Cu043b%5Cu043e%5Cu043d%5Cu043e%5Cu0432%5Cu0441%5Cu043a%5Cu0438%5Cu0439+%5Cu043f%22%7D',
    'Уфа': '%7B%22id%22%3A%2274%22%2C%22name%22%3A%22%5Cu0423%5Cu0444%5Cu0430%22%7D',
    'Нефтекамск': '%7B%22id%22%3A%2254973%22%2C%22name%22%3A%22%5Cu041d%5Cu0435%5Cu0444%5Cu0442%5Cu0435%5Cu043a%5Cu0430%5Cu043c%5Cu0441%5Cu043a%22%7D',
    'Стерлитамак': '%7B%22id%22%3A%2254975%22%2C%22name%22%3A%22%5Cu0421%5Cu0442%5Cu0435%5Cu0440%5Cu043b%5Cu0438%5Cu0442%5Cu0430%5Cu043c%5Cu0430%5Cu043a%22%7D',
    'Йошкар-Ола': '%7B%22id%22%3A%2271759%22%2C%22name%22%3A%22%5Cu0419%5Cu043e%5Cu0448%5Cu043a%5Cu0430%5Cu0440-%5Cu041e%5Cu043b%5Cu0430%22%7D',
    'Волжск': '%7B%22id%22%3A%22103521%22%2C%22name%22%3A%22%5Cu0412%5Cu043e%5Cu043b%5Cu0436%5Cu0441%5Cu043a%22%7D',
    'Саранск': '%7B%22id%22%3A%2277%22%2C%22name%22%3A%22%5Cu0421%5Cu0430%5Cu0440%5Cu0430%5Cu043d%5Cu0441%5Cu043a%22%7D',
    'Рузаевка': '%7B%22id%22%3A%2254952%22%2C%22name%22%3A%22%5Cu0420%5Cu0443%5Cu0437%5Cu0430%5Cu0435%5Cu0432%5Cu043a%5Cu0430%22%7D',
    'Ковылкино': '%7B%22id%22%3A%2254957%22%2C%22name%22%3A%22%5Cu041a%5Cu043e%5Cu0432%5Cu044b%5Cu043b%5Cu043a%5Cu0438%5Cu043d%5Cu043e%22%7D',
    'Казань': '%7B%22id%22%3A%227%22%2C%22name%22%3A%22%5Cu041a%5Cu0430%5Cu0437%5Cu0430%5Cu043d%5Cu044c%22%7D',
    'Набережные Челны': '%7B%22id%22%3A%228%22%2C%22name%22%3A%22%5Cu041d%5Cu0430%5Cu0431%5Cu0435%5Cu0440%5Cu0435%5Cu0436%5Cu043d%5Cu044b%5Cu0435+%5Cu0427%5Cu0435%5Cu043b%5Cu043d%5Cu044b%22%7D',
    'Бугульма': '%7B%22id%22%3A%2279%22%2C%22name%22%3A%22%5Cu0411%5Cu0443%5Cu0433%5Cu0443%5Cu043b%5Cu044c%5Cu043c%5Cu0430%22%7D',
    'Ростов-на-Дону': '%7B%22id%22%3A%2263214%22%2C%22name%22%3A%22%5Cu0420%5Cu043e%5Cu0441%5Cu0442%5Cu043e%5Cu0432-%5Cu043d%5Cu0430-%5Cu0414%5Cu043e%5Cu043d%5Cu0443%22%7D',
    'Шахты': '%7B%22id%22%3A%2272884%22%2C%22name%22%3A%22%5Cu0428%5Cu0430%5Cu0445%5Cu0442%5Cu044b%22%7D',
    'Волгодонск': '%7B%22id%22%3A%22102309%22%2C%22name%22%3A%22%5Cu0412%5Cu043e%5Cu043b%5Cu0433%5Cu043e%5Cu0434%5Cu043e%5Cu043d%5Cu0441%5Cu043a%22%7D',
    'Рязань': '%7B%22id%22%3A%2272125%22%2C%22name%22%3A%22%5Cu0420%5Cu044f%5Cu0437%5Cu0430%5Cu043d%5Cu044c%22%7D',
    'Самара': '%7B%22id%22%3A%221%22%2C%22name%22%3A%22%5Cu0421%5Cu0430%5Cu043c%5Cu0430%5Cu0440%5Cu0430%22%7D',
    'Тольятти': '%7B%22id%22%3A%222%22%2C%22name%22%3A%22%5Cu0422%5Cu043e%5Cu043b%5Cu044c%5Cu044f%5Cu0442%5Cu0442%5Cu0438%22%7D',
    'Сызрань': '%7B%22id%22%3A%2264%22%2C%22name%22%3A%22%5Cu0421%5Cu044b%5Cu0437%5Cu0440%5Cu0430%5Cu043d%5Cu044c%22%7D',
    'Санкт-Петербург': '%7B%22id%22%3A%2262195%22%2C%22name%22%3A%22%5Cu0421%5Cu0430%5Cu043d%5Cu043a%5Cu0442-%5Cu041f%5Cu0435%5Cu0442%5Cu0435%5Cu0440%5Cu0431%5Cu0443%5Cu0440%5Cu0433%22%7D',
    'Пушкин': '%7B%22id%22%3A%22133536%22%2C%22name%22%3A%22%5Cu041f%5Cu0443%5Cu0448%5Cu043a%5Cu0438%5Cu043d%22%7D',
    'Саратов': '%7B%22id%22%3A%224%22%2C%22name%22%3A%22%5Cu0421%5Cu0430%5Cu0440%5Cu0430%5Cu0442%5Cu043e%5Cu0432%22%7D',
    'Энгельс': '%7B%22id%22%3A%225%22%2C%22name%22%3A%22%5Cu042d%5Cu043d%5Cu0433%5Cu0435%5Cu043b%5Cu044c%5Cu0441%22%7D',
    'Балаково': '%7B%22id%22%3A%226%22%2C%22name%22%3A%22%5Cu0411%5Cu0430%5Cu043b%5Cu0430%5Cu043a%5Cu043e%5Cu0432%5Cu043e%22%7D',
    'Екатеринбург': '%7B%22id%22%3A%2259337%22%2C%22name%22%3A%22%5Cu0415%5Cu043a%5Cu0430%5Cu0442%5Cu0435%5Cu0440%5Cu0438%5Cu043d%5Cu0431%5Cu0443%5Cu0440%5Cu0433%22%7D',
    'Нижний Тагил': '%7B%22id%22%3A%2280969%22%2C%22name%22%3A%22%5Cu041d%5Cu0438%5Cu0436%5Cu043d%5Cu0438%5Cu0439+%5Cu0422%5Cu0430%5Cu0433%5Cu0438%5Cu043b%22%7D',
    'Верхняя Салда': '%7B%22id%22%3A%22100868%22%2C%22name%22%3A%22%5Cu0412%5Cu0435%5Cu0440%5Cu0445%5Cu043d%5Cu044f%5Cu044f+%5Cu0421%5Cu0430%5Cu043b%5Cu0434%5Cu0430%22%7D',
    'Смоленск': '%7B%22id%22%3A%2298790%22%2C%22name%22%3A%22%5Cu0421%5Cu043c%5Cu043e%5Cu043b%5Cu0435%5Cu043d%5Cu0441%5Cu043a%22%7D',
    'Сафоново': '%7B%22id%22%3A%22102692%22%2C%22name%22%3A%22%5Cu0421%5Cu0430%5Cu0444%5Cu043e%5Cu043d%5Cu043e%5Cu0432%5Cu043e%22%7D',
    'Ставрополь': '%7B%22id%22%3A%2280630%22%2C%22name%22%3A%22%5Cu0421%5Cu0442%5Cu0430%5Cu0432%5Cu0440%5Cu043e%5Cu043f%5Cu043e%5Cu043b%5Cu044c%22%7D',
    'Тамбов': '%7B%22id%22%3A%2299349%22%2C%22name%22%3A%22%5Cu0422%5Cu0430%5Cu043c%5Cu0431%5Cu043e%5Cu0432%22%7D',
    'Тверь': '%7B%22id%22%3A%2272925%22%2C%22name%22%3A%22%5Cu0422%5Cu0432%5Cu0435%5Cu0440%5Cu044c%22%7D',
    'Тула': '%7B%22id%22%3A%22133534%22%2C%22name%22%3A%22%5Cu0422%5Cu0443%5Cu043b%5Cu0430%22%7D',
    'Тюмень': '%7B%22id%22%3A%2280651%22%2C%22name%22%3A%22%5Cu0422%5Cu044e%5Cu043c%5Cu0435%5Cu043d%5Cu044c%22%7D',
    'Ульяновск': '%7B%22id%22%3A%2214%22%2C%22name%22%3A%22%5Cu0423%5Cu043b%5Cu044c%5Cu044f%5Cu043d%5Cu043e%5Cu0432%5Cu0441%5Cu043a%22%7D',
    'Димитровград': '%7B%22id%22%3A%2215%22%2C%22name%22%3A%22%5Cu0414%5Cu0438%5Cu043c%5Cu0438%5Cu0442%5Cu0440%5Cu043e%5Cu0432%5Cu0433%5Cu0440%5Cu0430%5Cu0434%22%7D',
    'Ишеевка': '%7B%22id%22%3A%22101189%22%2C%22name%22%3A%22%5Cu0440.%5Cu043f.%5Cu0418%5Cu0448%5Cu0435%5Cu0435%5Cu0432%5Cu043a%5Cu0430%22%7D',
    'Челябинск': '%7B%22id%22%3A%2259341%22%2C%22name%22%3A%22%5Cu0427%5Cu0435%5Cu043b%5Cu044f%5Cu0431%5Cu0438%5Cu043d%5Cu0441%5Cu043a%22%7D',
    'Магнитогорск': '%7B%22id%22%3A%22101923%22%2C%22name%22%3A%22%5Cu041c%5Cu0430%5Cu0433%5Cu043d%5Cu0438%5Cu0442%5Cu043e%5Cu0433%5Cu043e%5Cu0440%5Cu0441%5Cu043a%22%7D',
    'Златоуст': '%7B%22id%22%3A%2299623%22%2C%22name%22%3A%22%5Cu0417%5Cu043b%5Cu0430%5Cu0442%5Cu043e%5Cu0443%5Cu0441%5Cu0442%22%7D',
    'Чебоксары': '%7B%22id%22%3A%2262%22%2C%22name%22%3A%22%5Cu0427%5Cu0435%5Cu0431%5Cu043e%5Cu043a%5Cu0441%5Cu0430%5Cu0440%5Cu044b%22%7D',
    'Канаш': '%7B%22id%22%3A%2254972%22%2C%22name%22%3A%22%5Cu041a%5Cu0430%5Cu043d%5Cu0430%5Cu0448%22%7D',
    'Ярославль': '%7B%22id%22%3A%2258715%22%2C%22name%22%3A%22%5Cu042f%5Cu0440%5Cu043e%5Cu0441%5Cu043b%5Cu0430%5Cu0432%5Cu043b%5Cu044c%22%7D',
    'Рыбинск': '%7B%22id%22%3A%2271670%22%2C%22name%22%3A%22%5Cu0420%5Cu044b%5Cu0431%5Cu0438%5Cu043d%5Cu0441%5Cu043a%22%7D',
    'Переславль-Залесский': '%7B%22id%22%3A%2262968%22%2C%22name%22%3A%22%5Cu041f%5Cu0435%5Cu0440%5Cu0435%5Cu0441%5Cu043b%5Cu0430%5Cu0432%5Cu043b%5Cu044c-%5Cu0417%5Cu0430%5Cu043b%5Cu0435%5Cu0441%5Cu0441%5Cu043a%5Cu0438%5Cu0439%22%7D',
}

cats = {
    '836': '4297', '3706': '6297', '804': '2135', '1121': '10419', '877': '14300', '1244': '3729', '1167': '6159', '898': '23244', '911': '25600', '1128': '6990', '1154': '19979',
    '920': '3769', '1158': '2515', '1035': '117810', '1028': '8226', '1086': '30769', '1132': '14897', '1101': '4338', '963': '229', '1172': '40500', '860': '13477', '1214': '2868', '1024': '10150', '1148': '120156', '1230': '10197', '931': '999', '2446': '8010', '2458': '5431', '2488': '5020', '2551': '4769', '2567': '8620', '2586': '3179', '3730': '1609', '3735': '1799', '1248': '418', '2863': '2699', '2879': '1749', '2888': '4939', '2944': '2099', '2947': '8639', '2951': '2519', '2977': '1919', '2983': '407', '2986': '2409', '3011': '723', '990': '4001', '996': '7049', '1001': '4800', '1002': '8340', '1005': '14309', '1011': '5820', '1012': '9059', '1013': '779', '1014': '57241', '1015': '399',
    '3715': '4297', '3718': '36518', '3719': '914', '1187': '4100', '1189': '3860', '1190': '5780', '1191': '13719', '1192': '13690', '1198': '5489', '1199': '8690', '1200': '10799', '1207': '3015', '3708': '11299', '3709': '16890'
}

for city in cities:
    result = pd.DataFrame()
    start = time.time()
    for cat_id in cats:
        result = parse_category(result, cities[city], city, {
            'id': int(cat_id),
            'max': int(cats[cat_id]),
        })

    with open('result/time.txt', 'a') as file:
        file.write('%s crawl time %f\n' % (city, time.time() - start))
        file.close()

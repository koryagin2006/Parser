from pathlib import Path
import codecs
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import time

host = 'https://gorzdrav.org/'

Path('raw').mkdir(parents=True, exist_ok=True)
Path('result').mkdir(parents=True, exist_ok=True)


cities = {
    "moscow": "Москва",
    #"aprelevka": "Апрелевка",
    "balashiha": "Балашиха",
    #"beloozerskij": "Белоозерский",
    #"bronnicy": "Бронницы",
    #"vidnoe": "Видное",
    #"volokolamsk": "Волоколамск",
    #"voskresensk": "Воскресенск",
    #"vysokovsk": "Высоковск",
    #"golicyno": "Голицыно",
    #"dedenevo": "Деденево",
    #"dzerzhinskij": "Дзержинский",
    #"dmitrov": "Дмитров",
    #"dolgoprudnyj": "Долгопрудный",
    #"domodedovo": "Домодедово",
    #"dubna": "Дубна",
    #"egorevsk": "Егорьевск",
    #"zhukovskij": "Жуковский",
    #"zaprudnya": "Запрудня",
    #"zvenigorod": "Звенигород",
    #"zelenograd": "Зеленоград",
    #"ivanteevka": "Ивантеевка",
    #"istra": "Истра",
    #"kashira": "Кашира",
    #"klin": "Клин",
    #"kolomna": "Коломна",
    #"korolev": "Королев",
    #"kraskovo": "Красково",
    #"krasnoarmejsk": "Красноармейск",
    #"krasnogorsk": "Красногорск",
    #"krasnoznamensk": "Краснознаменск",
    #"lobnya": "Лобня",
    #"losino-petrovskij": "Лосино-Петровский",
    #"luhovicy": "Луховицы",
    #"lytkarino": "Лыткарино",
    "lyubercy": "Люберцы",
    #"mozhajsk": "Можайск",
    #"moskovskij": "Московский",
    "mytishchi": "Мытищи",
    #"naro-fominsk": "Наро-Фоминск",
    #"noginsk": "Ногинск",
    #"odincovo": "Одинцово",
    #"oktyabrskij": "Октябрьский",
    #"orekhovo-zuevo": "Орехово-Зуево",
    #"pavlovskij-posad": "Павловский Посад",
    #"peresvet": "Пересвет",
    #"podolsk": "Подольск",
    #"pokrovskoe": "Покровское",
    #"protvino": "Протвино",
    #"pushkino": "Пушкино",
    #"pushchino": "Пущино",
    #"razvilkovskoe": "Развилковское",
    #"ramenskoe": "Раменское",
    #"reutov": "Реутов",
    #"roshal": "Рошаль",
    #"ruza": "Руза",
    #"semenovskoe": "Семеновское",
    #"sergiev-posad": "Сергиев Посад",
    #"serebryanye-prudy": "Серебряные Пруды",
    #"serpuhov": "Серпухов",
    #"solnechnogorsk": "Солнечногорск",
    #"stupino": "Ступино",
    #"taldom": "Талдом",
    #"tomilino": "Томилино",
    #"troick": "Троицк",
    #"tuchkovo": "Тучково",
    #"uvarovka": "Уваровка",
    #"fryanovo": "Фряново",
    #"himki": "Химки",
    #"chekhov": "Чехов",
    #"shatura": "Шатура",
    #"shchelkovo": "Щелково",
    "shcherbinka": "Щербинка",
    #"ehlektrostal": "Электросталь",
    "spb": "Санкт-Петербург"
    #"volhov": "Волхов",
    #"vyborg": "Выборг",
    #"gatchina": "Гатчина",
    #"kolpino": "Колпино",
    #"kondopoga": "Кондопога",
    #"krasnoe-selo": "Красное Село",
    #"kronshtadt": "Кронштадт",
    #"lomonosov": "Ломоносов",
    #"petergof": "Петергоф",
    #"svetogorsk": "Светогорск",
    #"sestroreck": "Сестрорецк"
}

categories = [
    "https://gorzdrav.org/%s/category/zdorovyj-obraz-zhizni/",
    "https://gorzdrav.org/%s/category/zdorove-glaz/",
    "https://gorzdrav.org/%s/category/zdorove-nervnoj-sistemy/",
    "https://gorzdrav.org/%s/category/profilaktika-i-lechenie-orvi/",
    "https://gorzdrav.org/%s/category/zdorove-serdca-i-sosudov/",
    "https://gorzdrav.org/%s/category/zdorove-sistemy-pishhevarenija/",
    "https://gorzdrav.org/%s/category/zdorove-skeletnomyshechnoj-sistemy/",
    "https://gorzdrav.org/%s/category/vse-dlja-mamy-i-malysha/",
    "https://gorzdrav.org/%s/category/gigiena-i-kosmetika/",
    "https://gorzdrav.org/%s/category/drugie-preparaty/",
    "https://gorzdrav.org/%s/category/medicinskaja-tekhnika-i-predmety-ukhoda/",
    "https://gorzdrav.org/%s/category/ortopedicheskie-tovary/"
]

def parse_product(product, city_title):
    if product == None:
        return

    title = product.find('div', {'class': 'c-prod-item__title'})
    if title == None:
        return

    price = product.find('span', {'class': 'b-price'})
    if price == None:
            return

    price = price.find('meta').get('content').strip()

    res = pd.DataFrame()
    return res.append(pd.DataFrame([[city_title, title.text.strip(), price, price]], columns = ['city', 'title', 'price_min', 'price_max']), ignore_index=True)


def parse_category(df, city_id, city, category_href):
    def grep(page_href):
        r = requests.get(page_href)
        catalog = BeautifulSoup(r.text, features='html.parser')

        return {
            'products': catalog.find_all('div', {'class': 'c-prod-item'}),
            'last': catalog.find('a', {'class': 'js-pager-next'}) == None
        }

    r = requests.get(category_href)
    page = BeautifulSoup(r.text, features='html.parser')


    for i in range(1, 100):
        print('%s?q=AvailableInStoresOrStock=true&page=%d' % (category_href, i))
        data = grep('%s?q=AvailableInStoresOrStock=true&page=%d' % (category_href, i))

        for product in data['products']:
            df = df.append(parse_product(product, city), ignore_index=True)
            df.to_csv('result/%s.csv' % city)
            time.sleep(.5)

        if data['last']:
            return df

    return df

for city_id in cities:
    result = pd.DataFrame()
    for category in categories:
        result = parse_category(result, city_id, cities[city_id], category % city_id)

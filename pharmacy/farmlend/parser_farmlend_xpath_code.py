import requests
from lxml import html
from pymongo import MongoClient
from pandas import read_excel
from datetime import datetime

start_time = datetime.today()

# path = 'Бланк мониторинга c кодами Фармленда.xls'
path = 'Бланк мониторинга Осень2020 расширc с кодами ФЛ.xls'

# Запуск сервера
try:
    client = MongoClient('localhost', 27017)
    print('connected successfully')
except Exception:
    print('bad connection')

# db = client['monitoring_price']  # создание БД
collection = client['monitoring_price'].farmlend_by_code  # Создание коллекции


# Подготовка списка позиций
# path = 'Бланк мониторинга АФИ Зима2020_с артикулами ФЛ.xls'
# df_0 = pd.read_excel(path)
# df_0 = df_0['Артикул Фармленд'].dropna().astype('int')
# product_list = list(df_0)

def position_list(path):
    """
    Функция преобразует из Excel в четкий список с артикулами Фармленда
    :param path: список из Excel
    :return: список артикулов ФАРМЛЕНД
    """
    df_0 = read_excel(path)
    df_0 = df_0['Артикул Фармленд'].dropna().astype('int')
    product_list = list(df_0)
    return product_list


def tree(main_link):
    """Функция возвращает распарсеную страницу сайта
    :param main_link: адрес ссылки
    """
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/80.0.3987.132 Safari/537.36'}
    response = requests.get(main_link, headers=header).text
    tree = html.fromstring(response)
    return tree


# Список городов.
towns = {
    # '/orenburg': 'Оренбург',
    # '/buguruslan': 'Бугуруслан',
    # '/buzuluk': 'Бузулук',
    # '/kuvandyk': 'Кувандык',
    # '/kumertau': 'Кумертау',
    # '/gai': 'Гай',
    # '/mednogorsk': 'Медногорск',
    # '/orsk': 'Орск',
    # '/birsk': 'Бирск',
    # '/ufa': 'Уфа',
    '/yanaul': 'Янаул',
}

product_list = position_list(path=path)
length_towns = len(towns)
length = len(towns) * len(product_list)

for town in towns:
    for product in product_list:
        length -= 1
        print(f'Осталось всего {length} позиций, сейчас в работе город {towns[town]}')
        product_link = f'https://farmlend.ru{town}/product/' + str(product)
        print(product_link)
        try:
            name = tree(product_link).xpath("//h1[@class='title m-t-0 m-b-20']/text()")[0]
            print(name)
            manufacturer = \
                tree(product_link).xpath("//div[@class='p-specifications m-b-20']/div[2]//a[@class='link']/text()")[0]
            articul = tree(product_link).xpath("//div[@class='p-specifications m-b-20']/div[1]//div[2]/text()")[0]
            articul = int(articul)
            # print(name, '\n', manufacturer)

            apteka_list = tree(product_link).xpath("//div[@class='pv-body']/div[@class='pv-item to-map']")
            for apteka in apteka_list:
                address = apteka.xpath(".//a/text()")[0]
                price = apteka.xpath(".//div[@class='f-col-3 hidden-xs-down']/span/text()")[0]
                price = float(price[:6].replace(',', '.'))

                drug_data = {'Aртикул': articul,
                             'Наименование': name,
                             'Производитель': manufacturer.replace("(", ""),
                             'Город': towns[town],
                             'Аптечная сеть': 'Фармленд',
                             'Адрес аптеки': address,
                             'Цена': str(price).replace('.', ','),
                             'Цена + 10%': str(round(price / 0.9, 1)).replace('.', ','),
                             'Дата мониторинга': str(datetime.today().date())
                             }
                print(drug_data)
                collection.insert_one(drug_data)
        except Exception:
            print("Не найден!")
            continue

print(f'Парсинг Фармленд окончен!\nВыполнено за {datetime.now() - start_time}')

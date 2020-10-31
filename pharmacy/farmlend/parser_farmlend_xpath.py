import requests
from lxml import html
from pymongo import MongoClient
import pandas as pd

# Запуск сервера
try:
    client = MongoClient('localhost', 27017)
    print('connected successfully')
except:
    print('bad connection')

db = client['farmlend']  # создание БД

# Подготовка списка позиций
path = 'Бланк мониторинга АФИ Зима2020_с артикулами ФЛ.xls'
df_0 = pd.read_excel(path)
df_0 = df_0['Наименование'].tolist()
length_pos = len(df_0)
print(f'Всего в списке {length_pos} позиций')

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/80.0.3987.132 Safari/537.36'}


def tree(main_link):
    response = requests.get(main_link, headers=header).text
    tree = html.fromstring(response)
    return tree


# Список городов. если комментарии, то - готово
towns = [
    'orenburg',
    'buguruslan',
    'buzuluk',
    'gai',
    'kuvandyk',
    'mednogorsk',
    'orsk',
    'kumertau'
]
length_towns = len(towns)

collection = db.farmlend_orenburg  # Создание коллекции

for town in towns:
    length_towns -= 1
    print(f'Осталось {length_towns} городов')

    for search in df_0:
        length_pos -= 1
        print(f'Осталось {length_pos} наименований')

        print(town + ":" + search)
        search_link = f'https://farmlend.ru/{town}/search?keyword={search}'
        product_list = tree(search_link) \
            .xpath("//div[@class='row row-sm']//div[@class='col-lg-3 col-md-4 col-xs-6 m-b-15']//a/@href")

        for product in product_list:
            # time.sleep(5)  # Приостановить выполнение программы на заданное количество секунд.

            product_link = 'https://farmlend.ru' + product
            print(product_link)
            try:
                name = tree(product_link).xpath("//h1[@class='title m-t-0 m-b-20']/text()")[0]
                manufacturer = tree(product_link).xpath(
                    "//div[@class='p-specifications m-b-20']/div[2]//a[@class='link']/text()")[0]
                articul = tree(product_link).xpath("//div[@class='p-specifications m-b-20']/div[1]//div[2]/text()")[0]
                articul = int(articul)
                # print(name, '\n', manufacturer)

                apteka_list = tree(product_link).xpath("//div[@class='pv-body']/div[@class='pv-item to-map']")
                for apteka in apteka_list:
                    address = apteka.xpath(".//a/text()")[0]
                    price = apteka.xpath(".//div[@class='f-col-3 hidden-xs-down']/span/text()")[0]
                    price = float(price[:6].replace(',', '.'))

                    drug_data = {'артикул': articul,
                                 'наименование': name,
                                 'производитель': manufacturer.replace("(", ""),
                                 'город': town,
                                 'адрес': address,
                                 'цена': price}

                    # print(drug_data)
                    #                     total_list.append(drug_data)
                    #                     print(drug_data)
                    collection.insert_one(drug_data)

            except Exception:
                continue

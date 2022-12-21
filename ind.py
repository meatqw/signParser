from db import add_item, get_item, get_all, update_section, update_tag, update_status
from resp import get_content, save
from wp import add_post
import re
import time

from transliterate import translit


BASE_URL = 'https://idn500.ru'
chars_for_delete = ['\n', '\r', '\t', '&nbsp', '\xa0']


def parsing_item(url):
    """GET INFO ABOUT ITEM"""

    content = get_content(url)

    if content:
        content = content.find('div', {'class': 'condensed-offsets'})

        # title
        title = content.find('h1', {'class': 'title'}).text.strip()

        # img
        img_links = content.find(
            'div', {'class': 'item-image-preview'})

        images = []
        if img_links:
            img_links = [i.get('src') for i in img_links.find_all('img')]
        elif content.find('div', {'class': 'item-image-original'}):
            img_links = [i.get('href') for i in content.find(
                'div', {'class': 'item-image-original'}).find_all('a')]
        else:
            img_links = []

        if len(img_links) != 0:
            for i in img_links:
                try:
                    if len(images) >= 3:
                        break

                    img_url = BASE_URL + i
                    img_id = img_url.split('/')[-1].split('.')[0]
                    img = save(BASE_URL, img_url, img_id, 'img')
                    if img:
                        images.append(img)

                except Exception as e:
                    print(url, 'NO IMAGE')
        else:
            print(url, 'NO IMAGE')
            images = None

        # price
        try:
            price = content.find(
                'b', {'class': 'external-price'}).text.replace(' ', '')
        except Exception as e:
            print(url, 'NO PRICE')
            price = 0

        # desc
        description_tabs = content.find(
            'div', {'class': 'description js-tabs'})

        description = ' '.join([i.text for i in description_tabs.find(
            'div', {'class': 'description-left col-md-6'}).find_all('p', recursive=False)]).translate(str.maketrans('', '', ''.join(chars_for_delete))).strip()
        
        if len(description) < 10:
            description = content.find('div', {'class': 'item-description'}).text.translate(str.maketrans('', '', ''.join(chars_for_delete))).strip()
            print(url, 'NO LONG DESCRIPTION')
        

        # fields
        field = description_tabs.find('div', {'id': 'tab-features'})
        field_item = field.find('div', {'class': 'item-description'})
        field_list = field_item.find('div', {'class': 'features-list'})
        fields = []
        for f in field_list.find_all('dl', {'class': 'features'}):
            name = f.find('dt', {'class': 'features__title'}).text.strip()
            value = f.find('dd', {'class': 'features_value'}).text.strip()
            field = {'name': name, 'value': value}
            fields.append(field)

        data = {'title': title, 'img': images, 'price': price,
                'description': description.strip(), 'fields': fields, 'link': url}

        return data


def parsing_all_items(url_data):
    """GET ALL DATA FROM ITEM LIST"""

    print(url_data['url'])

    content = get_content(url_data['url'])
    if content:
        items = content.find_all('div', {'class': 'col flex-column'})

        countNew = 0
        countUpdated = 0
        for item in items:
            link = item.find('a').get('href')
            data = parsing_item(BASE_URL + link)
            data['tag'] = url_data['tag']
            data['section'] = url_data['section']
            data['donor'] = BASE_URL
            data['status'] = False

            item_old = get_item(data['title'])
            if item_old == None:
                add_item(data)
                print('New data: ', data['link'])
                countNew += 1
            else:
                update_tag(item_old, url_data['tag'])
                update_section(item_old, url_data['section'])
                print(f"{data['link']} is already in the database")
                countUpdated += 1

        print(url_data['url'], url_data['cat_name'],
              f'Count new data: {countNew}', f"Count updated data: {countUpdated}")


urls = [
    # Дорожная отрасль
    {'url': 'https://idn500.ru/lezhachie_policeyskie/',
     'cat_name': 'Лежачие полицейские', 'tag': ['Сопутствующее'], 'section': ['Дорожная отрасль']},
    {'url': 'https://idn500.ru/sezd_s_bordyura/',
     'cat_name': 'Съезды с бордюров', 'tag': ['Сопутствующее'], 'section': ['Дорожная отрасль']},
    {'url': 'https://idn500.ru/deliniatory/',
     'cat_name': 'Делиниаторы', 'tag': ['Сопутствующее'], 'section': ['Дорожная отрасль']},
    {'url': 'https://idn500.ru/zerkala_dorozhnye/',
     'cat_name': 'Зеркала', 'tag': ['Сопутствующее'], 'section': ['Дорожная отрасль']},
    {'url': 'https://idn500.ru/svetofory_i_kontrollery/',
     'cat_name': 'Светофоры', 'tag': ['Сопутствующее'], 'section': ['Дорожная отрасль']},
    {'url': 'https://idn500.ru/materials/',
     'cat_name': 'Материалы для разметки', 'tag': ['Сопутствующее'], 'section': ['Дорожная отрасль']},
    # общественные заведения
    {'url': 'https://idn500.ru/kolesootboyniki/',
     'cat_name': 'Колесоотбойники', 'tag': ['Опоры'], 'section': ['Общественные заведения']},
    {'url': 'https://idn500.ru/kabel_kanaly/',
     'cat_name': 'Кабель каналы', 'tag': ['Опоры'], 'section': ['Общественные заведения']},
    {'url': 'https://idn500.ru/zashchita_sten_i_uglov/',
     'cat_name': 'Защита стен и углов', 'tag': ['Опоры'], 'section': ['Общественные заведения']},
    # Охрана труда
    {'url': 'https://idn500.ru/fencing/ribbons/',
     'cat_name': 'Сигнальные ленты', 'tag': ['Опоры'], 'section': ['Охрана труда']},
    # городская среда
    {'url': 'https://idn500.ru/metallokonstruktsii/veloparkovki/',
     'cat_name': 'Велопарковка', 'tag': ['Сопутствующее'], 'section': ['Городская среда']},
    {'url': 'https://idn500.ru/metallokonstruktsii/blokirator_parkovochnogo_mesta/',
     'cat_name': 'Блокираторы', 'tag': ['Сопутствующее'], 'section': ['Городская среда']},
    {'url': 'https://idn500.ru/lezhachie_policeyskie/',
     'cat_name': 'Лежачие полицейские', 'tag': ['Сопутствующее'], 'section': ['Городская среда']},
    {'url': 'https://idn500.ru/sezd_s_bordyura/',
     'cat_name': 'Съезды с бордюров', 'tag': ['Сопутствующее'], 'section': ['Городская среда']},
    {'url': 'https://idn500.ru/zerkala_dorozhnye/',
     'cat_name': 'Зеркала', 'tag': ['Сопутствующее'], 'section': ['Городская среда']},
    {'url': 'https://idn500.ru/kolesootboyniki/',
     'cat_name': 'Колесоотбойники', 'tag': ['Сопутствующее'], 'section': ['Городская среда']},
    {'url': 'https://idn500.ru/svetofory_i_kontrollery/',
     'cat_name': 'Светофоры', 'tag': ['Сопутствующее'], 'section': ['Городская среда']},
]


def add_items_in_base():
    """UPLOAD ITEMS IN BASE"""
    for url_data in urls:
        parsing_all_items(url_data)


def add_items_in_site():
    """UPLOAD ITEMS IN SITE"""
    for i in get_all(BASE_URL):
        data = {'id': i[0], 'link': i[1], 'title': i[2], 'description': i[3],
                'fields': i[4], 'price': int(i[5]), 'img': i[6], 'tag': i[7], 'section': i[8],
                'donor': i[9]}

        try:
            id = add_post(data)
            print(id)
            update_status(data['id'])
        except Exception as e:
            print(e)
            print(data)
            time.sleep(30)

add_items_in_site()

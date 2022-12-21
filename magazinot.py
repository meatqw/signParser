from db import add_item, get_item, get_all, update_section, update_tag, update_status
from resp import get_content, save
from wp import add_post
import re
import time

from transliterate import translit


BASE_URL = 'https://magazinot.ru'
chars_for_delete = ['\n', '\r', '\t', '&nbsp', '\xa0', '\u2009']


def parsing_item(url):
    """GET INFO ABOUT ITEM"""

    content = get_content(url)

    if content:
        content = content.find('div', {'id': 'content'})

        # title
        title = content.find('h1', {'itemprop': 'name'}).text.strip()

        # img
        img_links = content.find(
            'div', {'id': 'pr_photo'}).find_all('a', {'class': 'pr_mini_photo ps'})

        images = []

        if len(img_links) != 0:
            for i in img_links:
                try:
                    if len(images) >= 3:
                        break

                    img_url = BASE_URL + i.get('href')
                    img_id = img_url.split('|')[-1].split('.')[0]
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
                'div', {'id': 'gti_price'}).text.replace(' ₽', '').translate(str.maketrans('', '', ''.join(chars_for_delete)))
        except Exception as e:
            print(url, 'NO PRICE')
            price = 0

        # desc
        description_tab = content.find(
            'div', {'id': 'desc'}).find('div', {'class': 'p_change'}).find_all('p')[0:2]

        description = " ".join([i.text.replace(':', '').strip().translate(str.maketrans('', '', ''.join(chars_for_delete))) for i in description_tab])
        
    
        # fields
        field = content.find('div', {'id': 'ext_params'})
        fields = []
        for f in field.find_all('tr', {'class': 'ext_dotted'}):
            name = f.find('td', {'class': 'big_good_ext_data_name'}).text.strip().replace(':', '')
            value = f.find('td', {'class': 'big_good_ext_data_value'}).text.strip()
            field = {'name': name, 'value': value}
            fields.append(field)

        data = {'title': title, 'img': images, 'price': price,
                'description': description.strip(), 'fields': fields, 'link': url}

        return data


def group_links_parser(url):
    """Parsing links to a product that has multiple links"""

    links = []
    content = get_content(url)
    if content:
        items = content.find('table', {"class": "group_listing_table"}).find("tbody")
        for item in items.find_all('tr', {'class': 'tr_group_list'}):
            link = item.find('a', {'class': 'gl_enter'}).get('href')
            links.append(BASE_URL + link)
    
    return links


def parsing_all_items(url_data):
    """GET ALL DATA FROM ITEM LIST"""

    print(url_data['url'])

    content = get_content(url_data['url'])
    if content:
        items = content.find('div', {'class': 'pr_table'}).find_all('div', {'class': 'pr_block'})

        countNew = 0
        countUpdated = 0
        for item in items:
            link_ = item.find('a').get('href')

            type_link = item.find('a', {'class': 'to_cart group_button'})
            if type_link:
                links = group_links_parser(BASE_URL + link_)
            else:
                links = [BASE_URL + link]

            for link in links:
       
                data = parsing_item(link)
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
    #ПЛАКАТЫ
    {'url': 'https://magazinot.ru/ohrana-truda--uid-000206226/',
     'cat_name': 'Охрана труда', 'tag': ['Плакаты'], 'section': ['Охрана труда']},
    # {'url': 'https://magazinot.ru/pozharnaya-bezopasnost--uid-00066670/',
    #  'cat_name': 'Пожарная безопасность', 'tag': ['Плакаты'], 'section': ['Охрана труда']},
    # {'url': 'https://magazinot.ru/tehnika-bezopasnosti--uid-00066241/',
    #  'cat_name': 'Техника безопасности', 'tag': ['Плакаты'], 'section': ['Охрана труда']},
    # {'url': 'https://magazinot.ru/elektrobezopasnost--uid-00067005/',
    #  'cat_name': 'Электробезопасность', 'tag': ['Плакаты'], 'section': ['Охрана труда']},
    # {'url': 'https://magazinot.ru/meditsinskaya-pomosch--uid-00066612/',
    #  'cat_name': 'Медицинская помощь', 'tag': ['Плакаты'], 'section': ['Охрана труда']},
    # {'url': 'https://magazinot.ru/bezopasnost-v-stroitelstve--uid-00066828/',
    #  'cat_name': 'Безопасность в строительстве', 'tag': ['Плакаты'], 'section': ['Охрана труда']},
    # {'url': 'https://magazinot.ru/kompyuter-i-bezopasnost--uid-00066228/',
    #  'cat_name': 'Компьютер и безопасность', 'tag': ['Плакаты'], 'section': ['Охрана труда']},
    # {'url': 'https://magazinot.ru/bezopasnost-na-avtotransporte--uid-00065971/',
    #  'cat_name': 'Безопасность на автотранспорте', 'tag': ['Плакаты'], 'section': ['Дорожная отрасль']},

    # {'url': 'https://magazinot.ru/grazhdanskaya-oborona--uid-00066595/',
    #  'cat_name': 'Гражданская оборона', 'tag': ['Плакаты'], 'section': ['Городская среда']},
    # {'url': 'https://magazinot.ru/ohrana-okruzhayuschey-sredy--uid-00066715/',
    #  'cat_name': 'Охрана окружающей среды', 'tag': ['Плакаты'], 'section': ['Городская среда']},
    # {'url': 'https://magazinot.ru/drugie-temy--uid-0002223588/',
    #  'cat_name': 'Другие темы', 'tag': ['Плакаты'], 'section': ['Городская среда']},

    # {'url': 'https://magazinot.ru/plakaty-dlya-obrazovatelnyh-uchrezhdeniy--uid-0002235982/',
    #  'cat_name': 'Плакаты для образовательных учреждений', 'tag': ['Плакаты'], 'section': ['Общественные заведения']},
    # {'url': 'https://magazinot.ru/osnovy-bezopasnosti-zhiznedeyatelnosti--uid-0002235318/',
    #  'cat_name': 'ЗОЖ', 'tag': ['Плакаты'], 'section': ['Общественные заведения']},
    #   {'url': 'https://magazinot.ru/pozharnaya-bezopasnost--uid-00066670/',
    #  'cat_name': 'Пожарная безопасность', 'tag': ['Плакаты'], 'section': ['Общественные заведения']},
    #   {'url': 'https://magazinot.ru/meditsinskaya-pomosch--uid-00066612/',
    #  'cat_name': 'Медицинская помощь', 'tag': ['Плакаты'], 'section': ['Общественные заведения']},
    #  {'url': 'https://magazinot.ru/kompyuter-i-bezopasnost--uid-00066228/',
    #  'cat_name': 'Компьютер и безопасность  для ремонта дорог', 'tag': ['Плакаты'], 'section': ['Общественные заведения']},

    #  {'url': 'https://magazinot.ru/bezopasnost-na-zheleznoy-doroge--uid-00066522/',
    #  'cat_name': 'Безопасность на железной дороге', 'tag': ['Плакаты'], 'section': ['Транспортная безопасность']},
    #  {'url': 'https://magazinot.ru/bezopasnost-na-avtotransporte--uid-00065971/',
    #  'cat_name': 'Безопасность на автотранспорте', 'tag': ['Плакаты'], 'section': ['Транспортная безопасность']},

    #  {'url': 'https://magazinot.ru/pozharnaya-bezopasnost--uid-00066670/',
    #  'cat_name': 'Пожарная безопасность', 'tag': ['Плакаты'], 'section': ['Магистральные обозначения']},
    #  {'url': 'https://magazinot.ru/tehnika-bezopasnosti--uid-00066241/',
    #  'cat_name': 'Техника безопасности', 'tag': ['Плакаты'], 'section': ['Магистральные обозначения']},
    #  {'url': 'https://magazinot.ru/bezopasnost-v-stroitelstve--uid-00066828/',
    #  'cat_name': 'Безопасность в строительстве', 'tag': ['Плакаты'], 'section': ['Магистральные обозначения']},


    #  {'url': 'https://plasto.ru/viewpage.php?page_id=67',
    #  'cat_name': 'Светодиодные', 'tag': ['Знаки'], 'section': ['Дорожная отрасль']},
    #  {'url': 'https://plasto.ru/viewpage.php?page_id=208',
    #  'cat_name': 'Прицепы', 'tag': ['Знаки'], 'section': ['Дорожная отрасль']},
    #  {'url': 'https://plasto.ru/viewpage.php?page_id=486',
    #  'cat_name': 'Вертикальная разметка', 'tag': ['Знаки'], 'section': ['Дорожная отрасль']},
    #  {'url': 'https://plasto.ru/viewpage.php?page_id=109',
    #  'cat_name': 'Стойки для дорожных знаков', 'tag': ['Опоры'], 'section': ['Дорожная отрасль']},
    #  {'url': 'https://plasto.ru/viewpage.php?page_id=214',
    #  'cat_name': 'Раскладные опоры', 'tag': ['Опоры'], 'section': ['Дорожная отрасль']},
    #  {'url': 'https://plasto.ru/viewpage.php?page_id=489',
    #  'cat_name': 'Консольные опоры', 'tag': ['Опоры'], 'section': ['Дорожная отрасль']},
    #  {'url': 'https://plasto.ru/viewpage.php?page_id=115',
    #  'cat_name': 'Переносные опоры', 'tag': ['Опоры'], 'section': ['Дорожная отрасль']},
    #  {'url': 'https://plasto.ru/viewpage.php?page_id=167',
    #  'cat_name': 'Фундаменты', 'tag': ['Опоры'], 'section': ['Дорожная отрасль']},
    ]

def add_items_in_base():
    """UPLOAD ITEMS IN BASE"""
    for url_data in urls:
        parsing_all_items(url_data)


def add_items_in_site():
    """UPLOAD ITEMS IN SITE"""
    for num, i in enumerate(get_all(BASE_URL)):
        data = {'id': i[0], 'link': i[1], 'title': i[2], 'description': i[3],
                'fields': i[4], 'price': int(i[5]), 'img': i[6], 'tag': i[7], 'section': i[8],
                'donor': i[9]}

        try:
            id = add_post(data)
            print(id)
            update_status(data['id'])

            if num == 5:
                break
        except Exception as e:
            print(e)
            print(data)
            time.sleep(30)

add_items_in_site()
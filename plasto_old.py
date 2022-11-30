from db import add_item, get_item
from resp import get_content, save
from wp import add_post

from transliterate import translit


BASE_URL = 'https://plasto.ru'
chars_for_delete = ['\n', '\r', '\t', '&nbsp']


def parsing_item(url):
    """GET INFO ABOUT ITEM"""
    content = get_content(url)
    
    if content:
        

        try:
            head_content = content.find('div', {'class': 'head_product'})
            title = head_content.find('div', {'class': 'h2'}).text

            price = head_content.find('div', {'class': 'tacB price'})
            span_faw = price.find('span', {'class': 'faw'})
            price_div = price.find('div')

            if span_faw:
                span_faw.decompose()

            if price_div:
                price_div.decompose()

            price = price.text.replace(' ', '').replace('От', '').translate(
                str.maketrans('', '', ''.join(chars_for_delete)))

            # fields
            fields_content = head_content.find(
                'div', {'class': 'property exoL'}).find_all('div')
            fields = []
            for field in fields_content:
                field = [i.text for i in field.find_all('span')]
                fields.append({'name': field[0], 'value': field[1]})

            # images
            images_links = head_content.find(
                'div', {'class': 'photo'}).find_all('img')
            images = []
            for img in images_links:

                if BASE_URL not in img.get('src'):
                    img_url = BASE_URL + img.get('src')
                else:
                    img_url = img.get('src')

                img_id = img.get('src').split(
                    '/')[-1].split('.')[0].replace(' ', '_')
                img = save(BASE_URL, img_url, img_id, 'img')

                if img:
                    images.append(img)

            description = content.find('div', {'id': 'desc'}).text.translate(
                str.maketrans('', '', ''.join(chars_for_delete)))

            data = [{'title': title, 'img': images, 'price': price,
                     'description': description, 'fields': fields}]
            return data
        
        except:
            
            data = []
            content_list = content.find_all('div', {'class': 'element'})

            for el in content_list:
                info = el.find('div', {'class': 'info'})
                try:
                    title = info.find('big')
                    if title.find('b'):
                        title = title.find('b').text.translate(
                        str.maketrans('', '', ''.join(chars_for_delete)))
                    else:
                        title = info.find('big').text.translate(
                        str.maketrans('', '', ''.join(chars_for_delete)))
                except:
                    title = info.find('a').text.translate(
                        str.maketrans('', '', ''.join(chars_for_delete)))
                    
                # print(title)
                description = info.find('div', {'class': 'desc exoL'}).text.translate(
                    str.maketrans('', '', ''.join(chars_for_delete)))

                # price
                price = el.find('div', {'class': 'tacB price'})
                span_faw = price.find('span', {'class': 'faw'})
                price_div = price.find('div')

                if span_faw:
                    span_faw.decompose()

                if price_div:
                    price_div.decompose()

                price = price.text.replace(' ', '').replace(
                    'От', '').translate(str.maketrans('', '', ''.join(chars_for_delete)))

                # image
                img = el.find('div', {'class': 'pic'}).find('img')
                images = []
                if BASE_URL not in img.get('src'):
                    img_url = BASE_URL + img.get('src')
                else:
                    img_url = img.get('src')

                img_id = img.get('src').split(
                    '/')[-1].split('.')[0].replace(' ', '_')
                img = save(BASE_URL, img_url, img_id, 'img')

                if img:
                    images.append(img)

                # fields
                fields_content = el.find('div', {'class': 'params exoL'})
                exoB = fields_content.find('span', {'class': 'exoB'})
                if exoB:
                    exoB.decompose()

                try:
                    fields = []
                    for field in fields_content.text.translate(str.maketrans('', '', ''.join(chars_for_delete))).split(','):
                        field = [i for i in field.split(' - ')]
                        fields.append({'name': field[0], 'value': field[1]})
                except:
                    fields = [{'Габаритные размеры': el.find('div', {'class': 'params exoL'}).
                               text.strip().translate(str.maketrans('', '', ''.join(chars_for_delete)))}]

                data.append({'title': title, 'img': images, 'price': price,
                            'description': description, 'fields': fields})

            return data


def parsing_item_processing(link, url_data):
    print(link)
    try:
        datas = parsing_item(link)
    except Exception as e:
        print('No data')
        print(e)
        datas = []

    if len(datas) > 0:
        for data in datas:

            data['link'] = link
            data['tag'] = url_data['tag']
            data['section'] = url_data['section']
            data['donor'] = BASE_URL
            
            item = get_item(data['title'])
            
            if item is None:
                # add in DB
                add_item(data)
                
                print('New item:', data['title'])
                return True
            else:
                print(f"{data['title']} is already in the database")
                return False
    


def parsing_all_items(url_data):
    """GET ALL DATA FROM ITEM LIST"""
    print(url_data['url'])
    content = get_content(url_data['url'])
    if content:
        if content.find('div', {'class': 'tabs_content exoL'}):
            parsing_item_processing(url_data['url'], url_data)
        else:
            content_list = content.find_all('div', {'class': 'element'})

            links = [i.find('div', {'class': 'info'}).find(
                'a').get('href') for i in content_list]

            
            for link in links:
                    if BASE_URL not in link:
                        link = BASE_URL + link
                        
                    parsing_item_processing(link, url_data)

                    # post in WP
                    # id_post = add_post(data)
                    # print(id_post)
                

            

        print(url_data['url'], url_data['cat_name'])


urls = [
    # {'url': 'https://plasto.ru/viewpage.php?page_id=401',
    #  'cat_name': 'Дорожные барьеры', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    # {'url': 'https://plasto.ru/viewpage.php?page_id=89',
    #  'cat_name': 'Буферы', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    # {'url': 'https://plasto.ru/viewpage.php?page_id=127',
    #  'cat_name': 'Пластины', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    # {'url': 'https://plasto.ru/viewpage.php?page_id=396',
    #  'cat_name': 'Штакетные', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    # {'url': 'https://plasto.ru/viewpage.php?page_id=487',
    #  'cat_name': 'Типовые', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    # {'url': 'https://plasto.ru/viewpage.php?page_id=284',
    #  'cat_name': 'Пешеходные', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    # {'url': 'https://plasto.ru/viewpage.php?page_id=15',
    #  'cat_name': 'Конусы', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    # {'url': 'https://plasto.ru/viewpage.php?page_id=48',
    #  'cat_name': 'Фонари', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    # {'url': 'https://plasto.ru/viewpage.php?page_id=80',
    #  'cat_name': 'Парковочные столбики', 'tag': 'Опоры', 'section': ['Дорожная отрасль', 'Общественные заведения']},
    {'url': 'https://plasto.ru/viewpage.php?page_id=207',
     'cat_name': 'Паркинги', 'tag': 'Опоры', 'section': ['Дорожная отрасль', 'Общественные заведения']},
    # {'url': 'https://plasto.ru/viewpage.php?page_id=294',
    #  'cat_name': 'Строительные ограждения', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    # {'url': 'https://plasto.ru/viewpage.php?page_id=297',
    #  'cat_name': 'Муляжи ДПС', 'tag': 'Опоры', 'section': ['Дорожная отрасль']}
    ]

for url_data in urls:
    parsing_all_items(url_data)

# for i in parsing_item('https://plasto.ru/viewpage.php?page_id=65'):
#     print(i)

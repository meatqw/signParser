from db import add_item, get_item
from resp import get_content, save
from wp import add_post
import re

from transliterate import translit


BASE_URL = 'https://plasto.ru'
chars_for_delete = ['\n', '\r', '\t', '&nbsp']


def img_parsing(url):
    """PARSING ADDITIONAL IMG"""
    images = []
    try:
        content = get_content(url)
        if content:
            # images
            head_content = content.find('div', {'class': 'head_product'})
            images_links = head_content.find(
                'div', {'class': 'photo'}).find_all('img')
            
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
    except:
        pass
    
    return images


def parsing_all_items(url_data):
    """GET ALL DATA FROM ITEM LIST"""
    
    data = []
    print(url_data['url'])
    content = get_content(url_data['url'])
    if content:
        elements = content.find_all('div', {'class': 'element'})
        
        if len(elements) > 0:
        
            for element in elements:
                info = element.find('div', {'class': 'info'})
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
                    
                title = title.strip()
                if get_item(title) == None:
                    # print(title)
                    description = info.find('div', {'class': 'desc exoL'}).text.translate(
                        str.maketrans('', '', ''.join(chars_for_delete)))

                    # price
                    price = element.find('div', {'class': 'tacB price'})
                    span_faw = price.find('span', {'class': 'faw'})
                    price_div = price.find('div')

                    if span_faw:
                        span_faw.decompose()

                    if price_div:
                        price_div.decompose()

                    price = price.text.replace(' ', '').replace(
                        'От', '').translate(str.maketrans('', '', ''.join(chars_for_delete)))

                    # image
                    if element.find('div', {'class': 'pic pic_slider'}):
                        img = element.find('div', {'class': 'pic pic_slider'}).find('img')
                    else:
                        img = element.find('div', {'class': 'pic'}).find('img')
                        
                    images = []
                        
                    if BASE_URL not in img.get('src'):
                        if img.get('src')[0] != '/':
                            img_url = BASE_URL + '/' + img.get('src')
                        else:
                            img_url = BASE_URL + img.get('src')
                    else:
                        img_url = img.get('src')

                    img_id = img.get('src').split(
                        '/')[-1].split('.')[0].replace(' ', '_')
                    img = save(BASE_URL, img_url, img_id, 'img')

                    if img:
                        images.append(img)
                    
                    if info.find('a'):
                        link = info.find('a').get('href')
                        if BASE_URL not in link:
                            link = BASE_URL + link
                            for i in img_parsing(link):
                                if i not in images:
                                    images.append(i)
                    else:
                        link = None
                            
                    # fields
                    fields_content = element.find('div', {'class': 'params exoL'})
                    exoB = fields_content.find('span', {'class': 'exoB'})
                    if exoB:
                        exoB.decompose()

                    fields = []
                    field_text = fields_content.text.translate(str.maketrans('', '', ''.join(chars_for_delete)))
                    if field_text.count('-') > 2:
                        for i in re.findall(r'[А-Я]?[^А-Я]*', field_text):
                            field = i.split('-')
                            
                            if len(field) >= 2:
                                field = {'name': field[0].strip(), 'value': field[1].strip()}
                                fields.append(field)
                            
                    else:
                        fields = [{'name': 'Характеристики', 'value': field_text.strip()}]
                        

                    data.append({'title': title, 'img': images, 'price': price,
                                'description': description.strip(), 'fields': fields, "link": link})
                else:
                    print(f"{title} is already in the database")
                    
                    
        else:
            slider = content.find_all('div', {'class': 'specSlider'})
            if len(slider) > 0:
                slider = slider[0]
                
                items = slider.find_all('div', {'class': 'oneSpec'})
                
                description = content.find('div', {'id': 'desc'}).text.translate(
                    str.maketrans('', '', ''.join(chars_for_delete)))
                
                for element in items:
                    title = element.find('small', {'class': 'exoR'}).text.translate(
                            str.maketrans('', '', ''.join(chars_for_delete)))
                    
                    title = title.strip()
                    print(title)
                    if get_item(title) == None:
                    
                        # Price
                        price = element.find('big', {'class': 'tacB'})
                
                        span_faw = price.find('span', {'class': 'faw'})
                        price_div = price.find('div')

                        if span_faw:
                            span_faw.decompose()

                        if price_div:
                            price_div.decompose()
                            
                        price = price.text.replace(' ', '').replace(
                                'От', '').translate(str.maketrans('', '', ''.join(chars_for_delete)))
                        
                        link = url_data['url']
                        
                        images = []
                        
                        img = element.find('img')
                                
                        if BASE_URL not in img.get('src'):
                            if img.get('src')[0] != '/':
                                img_url = BASE_URL + '/' + img.get('src')
                            else:
                                img_url = BASE_URL + img.get('src')
                        else:
                            img_url = img.get('src')

                        img_id = img.get('src').split(
                            '/')[-1].split('.')[0].replace(' ', '_')
                        img = save(BASE_URL, img_url, img_id, 'img')

                        if img:
                            images.append(img)
                            
                        # fields
                        fields = element.find('span', {'class': 'sparams'}).text.strip().translate(str.maketrans('', '', ''.join(chars_for_delete)))
                        fields = [{'name': 'Характеристики', 'value': fields}]
                        
                        data.append({'title': title, 'img': images, 'price': price,
                                        'description': description.strip(), 'fields': fields, "link": link})
                        
                    else:
                        print(f"{title} is already in the database")
                
        return data
        
        
urls = [
    {'url': 'https://plasto.ru/viewpage.php?page_id=401',
     'cat_name': 'Дорожные барьеры', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    {'url': 'https://plasto.ru/viewpage.php?page_id=89',
     'cat_name': 'Буферы', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    {'url': 'https://plasto.ru/viewpage.php?page_id=127',
     'cat_name': 'Пластины', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    {'url': 'https://plasto.ru/viewpage.php?page_id=396',
     'cat_name': 'Штакетные', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    {'url': 'https://plasto.ru/viewpage.php?page_id=487',
     'cat_name': 'Типовые', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    {'url': 'https://plasto.ru/viewpage.php?page_id=284',
     'cat_name': 'Пешеходные', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    {'url': 'https://plasto.ru/viewpage.php?page_id=15',
     'cat_name': 'Конусы', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    {'url': 'https://plasto.ru/viewpage.php?page_id=48',
     'cat_name': 'Фонари', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    {'url': 'https://plasto.ru/viewpage.php?page_id=80',
     'cat_name': 'Парковочные столбики', 'tag': 'Опоры', 'section': ['Дорожная отрасль', 'Общественные заведения']},
    {'url': 'https://plasto.ru/viewpage.php?page_id=207',
     'cat_name': 'Паркинги', 'tag': 'Опоры', 'section': ['Дорожная отрасль', 'Общественные заведения']},
    {'url': 'https://plasto.ru/viewpage.php?page_id=294',
     'cat_name': 'Строительные ограждения', 'tag': 'Опоры', 'section': ['Дорожная отрасль']},
    {'url': 'https://plasto.ru/viewpage.php?page_id=297',
     'cat_name': 'Муляжи ДПС', 'tag': 'Опоры', 'section': ['Дорожная отрасль']}
    ]

for url_data in urls:
    datas = parsing_all_items(url_data)
    for data in datas:
        data['tag'] = url_data['tag']
        data['section'] = url_data['section']
        data['donor'] = BASE_URL
        # print(data)
        add_item(data)
    
    print(url_data['url'], url_data['cat_name'], f'Count: {len(datas)}')
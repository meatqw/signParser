from db import add_item
from resp import get_content, save
from wp import add_post

from transliterate import translit


BASE_URL = 'https://plasto.ru'
chars_for_delete = ['\n', '\r', '\t', '&nbsp']


def parsing_item(url):
    """GET INFO ABOUT ITEM"""
    content = get_content(url)
    if content:
        head_content = content.find('div', {'class': 'head_product'})

        if head_content.find('div', {'class': 'panel'}) is None:

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
        else:

            data = []
            content_list = content.find_all('div', {'class': 'element'})
            
            for el in content_list:
                info = el.find('div', {'class': 'info'})

                try:
                    title = info.find('big').text.translate(
                        str.maketrans('', '', ''.join(chars_for_delete)))
                except:
                    title = info.find('a').text.translate(
                        str.maketrans('', '', ''.join(chars_for_delete)))

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
                exoB.decompose()

                try:
                    fields = []
                    for field in fields_content.text.translate(str.maketrans('', '', ''.join(chars_for_delete))).split(','):
                        field = [i for i in field.split(' - ')]
                        fields.append({'name': field[0], 'value': field[1]})
                except:
                    fields = [{'Габаритные размеры': el.find('div', {'class': 'params exoL'}).
                    text.strip().translate(str.maketrans('', '', ''.join(chars_for_delete)))}]

                data.append({'title': title, 'img': images, 'price': price, 'description': description, 'fields': fields})

            return data


def parsing_all_items(url_data):
    """GET ALL DATA FROM ITEM LIST"""
    content = get_content(url_data['url'])
    links_list  = []
    if content:
        content_list = content.find_all('div', {'class': 'element'})

        links = [i.find('div', {'class': 'info'}).find(
            'a').get('href') for i in content_list]

        num = 0
        for link in links:
            link = BASE_URL + link

            if link not in links_list:
                links_list.append(link)
                print(link)
                try:
                    datas = parsing_item(link)
                except:
                    print('No data')
                    datas = []

                if len(datas) > 0:       
                    for data in datas:

                        data['link'] = link
                        data['tag'] = url_data['tag']
                        data['section'] = url_data['section']
                        data['donor'] = BASE_URL

                        # add in DB
                        add_item(data)

                        # post in WP
                        id_post = add_post(data)
                        print(id_post)

                        num += 1

            else:
                print(f"{link} is already in the database")

        print('url', num)


urls = [{'url': 'https://plasto.ru/viewpage.php?page_id=401',
         'cat_name': 'Дорожные барьеры', 'tag': 'Опоры', 'section': 'Дорожная отрасль'}]

# for url_data in urls:
#     parsing_all_items(url_data)

print(parsing_item('https://plasto.ru/viewpage.php?page_id=78'))

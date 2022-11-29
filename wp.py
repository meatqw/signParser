import requests
import base64
import os
from requests_toolbelt.multipart.encoder import MultipartEncoder
# from webApp import config
import config
# from webApp.wp_db import WpDB
from datetime import datetime
from datetime import timedelta

user = config.USER_WP
password = config.PASSWORD_WP
credentials = user + ':' + password
token = base64.b64encode(credentials.encode())
header = {'Authorization': 'Basic ' + token.decode('utf-8'),
          'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                        ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}


# TAGS PROCESSING
def tags_search(name):
    url = f"https://{config.DOMEN}/wp-json/wp/v2/tags?search={name}"

    resource_get = requests.get(url, headers=header)

    try:
        return resource_get.json()[0]['id']
    except:
        return None


def tags_create(name, local, con):
    url = f"https://{config.DOMEN}/wp-json/wp/v2/tags?name={name}"
    try:
        resource_get = requests.post(url, headers=header)
        id_tag = resource_get.json()['id']
        con.insert_relationships(id_tag, local+1)
        return id_tag
    except:
        return None


def tags_processing(name, local, con):
    if tags_search(name) is None:
        return tags_create(name, local, con)
    else:
        return tags_search(name)


def category_search(name):
    """CATEGORY SEARCH"""
    url = f"https://{config.DOMEN}/wp-json/wp/v2/categories?search={name}"

    resource_get = requests.get(url, headers=header)

    try:
        return resource_get.json()[0]['id']
    except:
        return None


def add_post(data):
    """ADD POST PROCESSING"""
    category = ["1", f'{category_search(data["section"])}']

    tag = [f'{tags_search(data["tag"])}']

    # upload image on wp media
    # return id img
    if len(data['img']) == 1:
        try:
            id_img = upload_media(f"{data['img'][0]}")
            featured_media = id_img
            gal_img = [{'prod_first_gal_img': id_img}]
        except:
            id_img = None
    else:
        gal_img = []
        for num, img in enumerate(data['img']):
            id_img = upload_media(img)
            if num == 0:
                featured_media = id_img
            gal_img.append({'prod_first_gal_img': id_img})
            if num == 2:
                break

    # fields
    fields = []
    if data['fields'] and len(data['fields']) > 0:
        for field in data['fields']:
            fields.append({
                        "prod_first_list_head": field['name'],
                        "prod_first_list_val": field['value']
                        })
    
            

    # posting new post
    url = f"https://{config.DOMEN}/wp-json/wp/v2/posts"

    post = {
        'title': f'{data["title"]}',
        'status': 'publish',
        'categories': category,
        'tags': tag,
        'content': data['description'],
        'featured_media': featured_media,
        "acf": {
            "prod_first_price": f"{data['price']}р.",
            "prod_first_list": fields,
            "prod_first_gal": gal_img,
            "prod_fut_head": "Наши преимущества",
            "prod_fut_list": [
                {
                    "prod_fut_list_txt": "Опыт работы с 2003г.",
                    "prod_fut_list_icon": 84
                },
                {
                    "prod_fut_list_txt": "Поставляем по всей России",
                    "prod_fut_list_icon": 85
                },
                {
                    "prod_fut_list_txt": "Собственное производство 80%",
                    "prod_fut_list_icon": 86
                },
                {
                    "prod_fut_list_txt": "Дилеры ведущих производителей",
                    "prod_fut_list_icon": 87
                },
                {
                    "prod_fut_list_txt": "Участвуем в тендерах",
                    "prod_fut_list_icon": 88
                },
                {
                    "prod_fut_list_txt": "Очень доступная цена",
                    "prod_fut_list_icon": 89
                },
                {
                    "prod_fut_list_txt": "Расширенная гарантия",
                    "prod_fut_list_icon": 90
                },
                {
                    "prod_fut_list_txt": "Доставка за наш счет!",
                    "prod_fut_list_icon": 91
                }
            ],
            "prod_related_head": None,
            "prod_related_prod": None,
            "prod_serv_list1": None,
            "prod_serv_list2": None
        },
    }
    # print(post)

    if id_img is not None:

        resource_post = requests.post(url, headers=header, json=post)
        # print(resource_post.json())
        id_ = resource_post.json()['id']

        return id_
    else:
        return None


def upload_media(filename):
    """UPLOAD MEDIA TO SITE"""
    file_name = os.path.basename(f'{filename}')
    multipart_data = MultipartEncoder(
        fields={
            'file': (file_name, open(f'{filename}', 'rb'), 'image/jpg'),
            'alt_text': 'sign',
            'caption': '',
            'description': ''
        }
    )
    header_ = {'Content-Type': multipart_data.content_type,
               'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                             ' (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}

    response = requests.post(f'https://{config.DOMEN}/wp-json/wp/v2/media', data=multipart_data,
                             headers=header_, auth=(config.USER_WP, config.PASSWORD_WP))

    return response.json()['id']


def get_posts():
    """GET ALL POSTS"""
    url = f"https://{config.DOMEN}/wp-json/wp/v2/posts?per_page=100"

    resource_get = requests.get(url, headers=header)
    return resource_get.json()


# print(len(get_news()))
# for i in get_posts()[:-1]:
#     print(i)
# print(tags_search('Знаки'))
# print(category_search('Транспортная безопасность'))


def del_media_request(id_):
    url = f"https://{config.DOMEN}/wp-json/wp/v2/media/{id_}?force=true"
    requests.delete(url, headers=header)


def del_media():
    """DEL MEDIA (MAYBE NOT WORK)"""
    for i in range(40):
        url = f"https://{config.DOMEN}/wp-json/wp/v2/media?per_page=100&page={i + 1}"
        now_date = datetime.now() - timedelta(days=2)
        print(now_date)
        resource_get = requests.get(url, headers=header)
        for i in resource_get.json():
            print(i)
            date = i['date']
            author = i['author']
            date = datetime.strptime(date.split('T')[0], "%Y-%m-%d")
            if (date < now_date) and author == 2:
                id_ = i['id']
                # del_media_request(id_)



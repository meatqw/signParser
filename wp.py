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


def add_post(title, description, filename, tags, category):
    """ADD POST PROCESSING"""
    category = [f'{category_search(category)}']

    tag = [f'{tags_search(tags)}']

    # upload image on wp media
    # return id img
    try:
        id_img = upload_media(f"{filename}")
    except:
        id_img = None

    # posting new post
    url = f"https://{config.DOMEN}/wp-json/wp/v2/posts"

    post = {
        'title': f'{title}',
        'status': 'draft',
        'types': category,
        'tags': tag,
        'content': description,
        # 'date': str(datetime.now()),
        # 'fields': {'source-news': f'{source}', 'datav-news': f'{str(datav)}',
        #            'descript-news': f'{descript}', 'text-news': f'{text}'},
        'featured_media': id_img
    }
    print(post)

    if id_img is not None:

        resource_post = requests.post(url, headers=header, json=post)
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


data = {'title': 'Расхождение и обгон запрещены!', 'img': 'img/Rashozhdenie_i_obgon_zaprescheny_2.jpg', 'price': '35000', 'description': 'Для обозначения участка судового хода, где обгон и расхождение судов запрещены.',
        'link': 'http://www.navitel-spb.ru/katalog/znaki-vnutrennikh-vodnykh-putey/raskhozhdenie-i-obgon-zapreshcheny/', 'tag': 'Знаки', 'section': 'Транспортная безопасность', 'donor': 'http://www.navitel-spb.ru'}



post = add_post(data['title'], data['img'], data['tag'], data['section'])

print(post)

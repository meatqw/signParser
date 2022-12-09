from db import add_item, get_all, update_status, update_section, update_tag
from resp import get_content, save
from wp import add_post
BASE_URL = 'http://www.navitel-spb.ru'
from transliterate import translit
import time


def parsing_item(url):
    """GET INFO ABOUT ITEM"""
    content = get_content(url)
    if content:
        content = content.find('div', {'class': 'catalog-element'})
        
        cat_top = content.find('div', {'class': 'cat-top'})
        
        title = content.find('h1').text
        img = BASE_URL + content.find('img').get('src')
        
        try:
            price = content.find('span', {'class': 'catalog-price'}).text.replace(' ', '').replace('руб.', '')
        except Exception as e:
            print(e)
            price = None
            
        cat_top.decompose()
        for i in content.find_all('a'):
            i.decompose()
        
        description = content.text.replace('\n', '').replace('\r', '').replace('\xa0', '').replace('\t', '')
        
        img_id = translit(img.split('/')[-1].split('.')[0].replace(' ', '_'), reversed=True)
        img = save(BASE_URL, img, img_id, 'img')
        
        data = {'title': title, 'img': [img], 'price': price, 'description': description}
        return data
        
    

def parsing_all_items(url):
    """GET ALL DATA FROM ITEM LIST"""
    content = get_content(url)
    if content:
        content_list = content.find('div', {'class': 'catalog-section'})
        
        links = content_list.find_all('td', {'class': 'imgcell'})

        num = 0
        for link in links:
            link = BASE_URL + link.find('a').get('href')
            data = parsing_item(link)
            
            data['link'] = link
            data['tag'] = ['Знаки']
            data['section'] = ['Транспортная безопасность']
            data['donor'] = BASE_URL
            data['fields'] = []
            data['status'] = False
            add_item(data)
            # id_post = add_post(data)
            # print(id_post)
            num += 1

            print(url, num)
            
            
url = ['http://www.navitel-spb.ru/katalog/znaki-vnutrennikh-vodnykh-putey/', 'http://www.navitel-spb.ru/katalog/navigatsionnye-znaki-dlya-rek/']
for i in url:
    parsing_all_items(i)

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
            

    
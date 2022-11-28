from db import add_item
from resp import get_content, save
from wp import add_post
BASE_URL = 'http://www.navitel-spb.ru'
from transliterate import translit


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
        for link in links:
            link = BASE_URL + link.find('a').get('href')
            data = parsing_item(link)
            
            data['link'] = link
            data['tag'] = 'Знаки'
            data['section'] = 'Транспортная безопасность'
            data['donor'] = BASE_URL
            add_item(data)
            add_post(data)
            
            
url = ['http://www.navitel-spb.ru/katalog/znaki-vnutrennikh-vodnykh-putey/', 'http://www.navitel-spb.ru/katalog/navigatsionnye-znaki-dlya-rek/']
for i in url:
    parsing_all_items(i)
    
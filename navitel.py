import requests
from bs4 import BeautifulSoup
from db import add_item

BASE_URL = 'http://www.navitel-spb.ru'

def get_content(url):
    try:
        request = requests.get(url, headers=headers)
        # redirect check
        if request.status_code == 200:
            content = BeautifulSoup(request.content, 'html.parser')
            return content
        else:
            print(request.status_code)
            return False

    except Exception as e:
        print(e)
        return False

headers = {"accept": "*/*",
           "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36"}

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
        
        data = {'title': title, 'img': img, 'price': price, 'description': description}
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
            data['tag'] = 'знаки'
            data['section'] = 'транспортная безопасность'
            data['donor'] = BASE_URL
            add_item(data)
            print(data)
            
            
        
        
    
    



url = ['http://www.navitel-spb.ru/katalog/znaki-vnutrennikh-vodnykh-putey/', 'http://www.navitel-spb.ru/katalog/navigatsionnye-znaki-dlya-rek/']
for i in url:
    parsing_all_items(i)
    
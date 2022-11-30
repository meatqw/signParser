import requests
from bs4 import BeautifulSoup

headers = {"accept": "*/*",
           "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36."}

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


def save(url, url_img, img_id, path):
    headers['referer'] = url
    req = requests.get(url_img, stream=True, headers=headers)
    if req.status_code == 200:
        with open(f"{path}/{img_id}.jpg", 'wb') as fd:
            for chunk in req.iter_content(4028):
                fd.write(chunk)
            fd.close()
            
        return f'{path}/{img_id}.jpg'
    else:
         
        return False

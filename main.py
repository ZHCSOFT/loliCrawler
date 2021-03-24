import requests
from bs4 import BeautifulSoup
import urllib
import os


def get_picture(target_url) -> str:
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/65.0.3325.146 Safari/537.36'
    }
    res = requests.get(target_url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')
    try:
        pic_block = soup.find('div', {'id': 'content'}).find('div', {'class': 'content', 'id': 'right-col'})\
            .find('img', {'id': 'image'})

        pic_url = pic_block.get('src')
        return pic_url

    except AttributeError as e:
        print('Error!', e)


def get_sub_pictures(target_url) -> list:
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/65.0.3325.146 Safari/537.36'
    }
    res = requests.get(target_url, headers=headers)
    pic_url_list = []
    soup = BeautifulSoup(res.text, 'lxml')

    try:
        pic_blocks = soup.find('div', {'id': 'content'}).find('div', {'class': 'content'}).find_all('li')
        for pic_block in pic_blocks:
            pic_url = pic_block.find('a').get('href')
            pic_url_list.append('https://yande.re' + pic_url)
    except AttributeError as e:
        print('Error!', e)

    return pic_url_list


def get_last_page(target_url) -> int:
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/65.0.3325.146 Safari/537.36'
    }
    last_page = 0
    res = requests.get(target_url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')

    try:
        page_blocks = soup.find('div', {'id': 'content'}).find('div', {'id': 'paginator'}).find_all('a')
        for page_block in page_blocks:
            page_label = page_block.get('aria-label')
            if page_label is not None:
                page_label_list = page_label.split()
                if page_label_list[0] == 'Page':
                    last_page = int(page_label_list[1])

    except AttributeError as e:
        print('Error!', e)

    return last_page


if __name__ == '__main__':
    lastPage = get_last_page('https://yande.re/post')
    file_id = 1
    for i in range(1, lastPage+1):
        url = 'https://yande.re/post?page=' + str(i)
        subPicList = get_sub_pictures(url)
        print('Page', i, 'Get', len(subPicList))

        for subPic in subPicList:
            picture = get_picture(subPic)
            filepath_name = '{}{}{}{}'.format('D:/Dataset/loli/', os.sep, str(file_id).zfill(8), '_pic.jpg')
            urllib.request.urlretrieve(picture, filename=filepath_name)
            file_id = file_id + 1

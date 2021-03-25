import os
import requests
from bs4 import BeautifulSoup
import urllib
from concurrent.futures import ThreadPoolExecutor


def get_info(target_url) -> dict:
    info = {}
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/65.0.3325.146 Safari/537.36'
    }
    res = requests.get(target_url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')
    try:
        content_blocks = soup.find('div', {'id': 'content'}).find('div', {'id': 'post-view'})\
            .find('div', {'id': 'stats', 'class': 'vote-container'}).find_all('li')
        for content_block in content_blocks:
            content = content_block.text
            text_list = content.split()
            if 'Id' in content:
                info.update({'id': int(text_list[-1])})
            elif 'Rating' in content:
                info.update({'rating': str(text_list[-1])})
        return info
    except Exception as e:
        print('Error!', e)
        return None
    return None


def download_picture(target_url, file_path, file_id, file_rating) -> int:

    file_name = '{}_{}_{}'.format(str(file_id).zfill(8), file_rating, 'pic.jpg')
    full_file_path = file_path+file_name
    try:
        if not os.path.exists(full_file_path):
            urllib.request.urlretrieve(target_url, filename=full_file_path)
        else:
            print('Duplicated file detected, ID =', file_id)
    except Exception as e:
        print('Error!', e)
        return 1
    return 0


def get_picture(target_url, high_res) -> str:
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/65.0.3325.146 Safari/537.36'
    }
    res = requests.get(target_url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')
    try:
        if high_res:
            sidebar_block = soup.find('div', {'id': 'content'}).find('div', {'id': 'post-view'}) \
                .find('div', {'class': 'sidebar'}).find('a', {'id': 'highres'})

            pic_url = sidebar_block.get('href')
            return pic_url
        else:
            pic_block = soup.find('div', {'id': 'content'}).find('div', {'class': 'content', 'id': 'right-col'}) \
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
        return 1
    return last_page


if __name__ == '__main__':
    lastPage = get_last_page('https://yande.re/post')
    print('Total page:', lastPage)
    filePath = 'D:/Dataset/loli/'

    if not os.path.exists(filePath):
        os.makedirs(filePath)

    with ThreadPoolExecutor(max_workers=16) as executor_1:
        with ThreadPoolExecutor(max_workers=16) as executor_2:
            for i in range(1, lastPage+1):
                url = 'https://yande.re/post?page=' + str(i)
                thread_1 = executor_1.submit(get_sub_pictures, url)
                sub_pic_list = thread_1.result()
                print('Page', i, 'Get', len(sub_pic_list))
                for subPic in sub_pic_list:
                    picture_info = get_info(subPic)
                    picture_url = get_picture(subPic, high_res=True)
                    executor_2.submit(download_picture, picture_url, filePath, picture_info.get('id'),
                                      picture_info.get('rating'))

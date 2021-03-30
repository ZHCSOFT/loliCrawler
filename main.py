import os
import requests
from bs4 import BeautifulSoup
import urllib
from typing import Union
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed


def retry_download(target_url, file_path, file_id, file_rating) -> int:
    def _progress(block_num, block_size, total_size):
        sys.stdout.write('\r>> Retry Download. %s %.1f%%' % (file_name,
                                                             float(block_num * block_size) / float(total_size) * 100.0))
        sys.stdout.flush()

    file_name = '{}_{}_{}'.format(str(file_id).zfill(8), file_rating, 'pic.jpg')
    full_file_path = file_path + file_name

    if not os.path.exists(full_file_path):
        try:
            urllib.request.urlretrieve(target_url, full_file_path, _progress)
        except Exception as e:
            print('Retry error!', e, 'File ID =', file_id, 'URL =', target_url)
            return 1
        return 0
    else:
        print('Duplicated file detected, ID =', file_id)
        return 1


def get_info(target_url) -> dict:
    info = {}
    text_list = ''
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
            try:
                if 'Id:' in content:
                    info.update({'id': int(text_list[-1])})
                elif 'Rating:' in content:
                    info.update({'rating': str(text_list[-1])})
            except AttributeError as e:
                print('Doubted value detected, content =', content, 'In url =', target_url)
                continue

        return info
    except Exception as e:
        print('Error!', e, 'Content =', content)
        print('text_list =', text_list)
        return None


def download_picture(target_url, file_path, file_id, file_rating) -> int:

    file_name = '{}_{}_{}'.format(str(file_id).zfill(8), file_rating, 'pic.jpg')
    full_file_path = file_path+file_name
    try:
        if not os.path.exists(full_file_path):
            urllib.request.urlretrieve(target_url, filename=full_file_path)
            return 0
        else:
            print('Duplicated file detected, ID =', file_id)
            return 1
        return 1
    except Exception as e:
        print('Error!', e, 'File ID =', file_id, 'URL =', target_url)
        retry_download(target_url, file_path, file_id, file_rating)
        return 1


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


def get_sub_pictures(current_page, target_url) -> Union[int, list]:
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
        return current_page, pic_url_list
    except AttributeError as e:
        print('Error!', e)


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
        return last_page
    except AttributeError as e:
        print('Error!', e)
        return 1


if __name__ == '__main__':
    lastPage = get_last_page('https://yande.re/post')
    print('Total page:', lastPage)
    filePath = 'D:/Dataset/loli_small/'
    if not os.path.exists(filePath):
        os.makedirs(filePath)

    thread1_list = []
    thread2_list = []
    startPage = 1
    max_workers = 16
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        inner_begin_page = startPage
        inner_end_page = startPage
        while inner_begin_page <= lastPage:
            if (inner_begin_page + max_workers) > (lastPage + 1):
                inner_end_page = lastPage + 1
            else:
                inner_end_page = inner_begin_page + max_workers

            for i in range(inner_begin_page, inner_end_page):
                url = 'https://yande.re/post?page=' + str(i)
                thread_1 = executor.submit(get_sub_pictures, i, url)
                thread1_list.append(thread_1)

            for one_thread in as_completed(thread1_list):
                currentPage, sub_pic_list = one_thread.result()
                print('Page', currentPage, 'Get', len(sub_pic_list))
                for subPic in sub_pic_list:
                    try:
                        picture_info = get_info(subPic)
                        picture_url = get_picture(subPic, high_res=False)
                        thread2 = executor.submit(download_picture, picture_url, filePath, picture_info.get('id'),
                                                  picture_info.get('rating'))
                        thread2_list.append(thread2)

                    except AttributeError as attr_e:
                        print('Error!', attr_e, 'subPic =', subPic)
                    except ConnectionError as conn_e:
                        print('Error!', conn_e, 'subPic =', subPic)
                as_completed(thread2_list)

            inner_begin_page = inner_end_page
            thread1_list = []
            thread2_list = []

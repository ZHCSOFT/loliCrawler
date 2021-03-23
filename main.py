import requests
from bs4 import BeautifulSoup
import urllib
import os


def getPicture(url) -> str:
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/65.0.3325.146 Safari/537.36'
    }
    res = requests.get(url, headers=headers)
    picURLList = []
    soup = BeautifulSoup(res.text, 'lxml')
    try:
        picBlock = soup.find('div', {'id': 'content'}).find('div', {'class': 'content', 'id': 'right-col'})\
            .find('img', {'id': 'image'})

        picURL = picBlock.get('src')
        return picURL

    except AttributeError as e:
        print('Error!', e)



def getSubPicList(url) -> list:
    # Use a breakpoint in the code line below to debug your script.
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                      ' Chrome/65.0.3325.146 Safari/537.36'
    }
    res = requests.get(url, headers=headers)
    picURLList = []
    soup = BeautifulSoup(res.text, 'lxml')

    try:
        picBlocks = soup.find('div', {'id': 'content'}).find('div', {'class': 'content'}).find_all('li')
        for picBlock in picBlocks:
            picURL = picBlock.find('a').get('href')
            picURLList.append('https://yande.re' + picURL)
    except AttributeError as e:
        print('Error!', e)

    return picURLList


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    file_id = 1
    for i in range(1, 16126):
        url = 'https://yande.re/post?page=' + str(i)
        subPicList = getSubPicList(url)
        print('Page', i, 'Get', len(subPicList))

        for subPic in subPicList:
            picture = getPicture(subPic)
            filepath_name = '{}{}{}{}'.format('D:/Dataset/loli/', os.sep, str(file_id).zfill(8), '_pic.jpg')
            urllib.request.urlretrieve(picture, filename=filepath_name)
            file_id = file_id + 1

import requests
import pymongo
import time
from bs4 import BeautifulSoup
import random
import csv

# 获取中国票房网国家代号
def get_area():
    urlmovie = 'http://www.cbooo.cn/movies'
    req = requests.get(urlmovie, headers=headers)
    html = req.text
    soup = BeautifulSoup(html, 'lxml')
    arealist = soup.find("select",id="selArea")
    # print(arealist)
    arealist = arealist.find_all("option")
    area_dic = {}
    # area_dic = []
    for i in arealist:
        # area_dic.append(i["value"])
        area_dic[i.get_text()] = i["value"]

    print(area_dic)
    with open('arealist.csv', 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for key, val in area_dic.items():
            print(repr(key), ':', repr(val))
            writer.writerow([key, val])

# 获取中国票房网一个国家的电影及票房数据
def get_data(area):
    client = pymongo.MongoClient()
    db = client.chinamovies
    collections = db.movies

    url_origin = 'http://www.cbooo.cn/Mdata/getMdata_movie?area={area}&type=0&year=2018&initial=%E5%85%A8%E9%83%A8&pIndex={page}'
    page = 1

    while True:
        url = url_origin.format(area=area[1], page=page)
        try:
            req = requests.get(url, headers=headers)
            data = req.json()
        except Exception as e:
            print(e)
            page += 1
            error_url.append(url)
            continue

        if data['tCount'] == 0:
            break
        time.sleep(2)
        print(url)
        collections.insert_many(data['pData'])
        page += 1
        if page > data['tPage']:
            print('page:',page)
            print("data['tPage']:",data['tPage'])
            print('area:',area)
            print('==========================================================================')
            break

# 获取中国票房网所有电影及票房
def get_cbooomovies():
    areadata = []
    with open('arealist.csv', 'r', encoding='utf-8') as areafile:
        reader = csv.reader(areafile)
        for item in reader:
            areadata.append(item)

    print(areadata)

    for area in areadata:
        print(area)
        get_data(area)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'Host': 'www.cbooo.cn',
    'Referer': 'http://www.cbooo.cn/movies',
}

error_url = []

# get_area()

# get_cbooomovies()

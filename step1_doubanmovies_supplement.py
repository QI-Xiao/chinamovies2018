import pymongo
import requests
from bs4 import BeautifulSoup
import time
import re
import random


def douban_detail(url_detail):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    }
    req = requests.get(url_detail,headers=headers)# , proxies=proxies
    soup = BeautifulSoup(req.text, 'lxml')
    releasedate = soup.find("div",id="info").find("span",property="v:initialReleaseDate",content=re.compile("2018.*"))
    name = soup.find("div", id="content").h1.find("span", property=True).string
    time.sleep(1.5+random.random())
    if releasedate:
        print(name, ': ', releasedate.string)
        if input('是否符合'):
            print('True')
            return True
    print('False')
    print(name, ': 没有信息')


def douban_api(moviename):
    # proxies = {'https':'1.192.241.250',}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Host': 'api.douban.com',
    }
    url_api = 'https://api.douban.com/v2/movie/search?q={}'.format(moviename)
    print(url_api)
    req = requests.get(url_api, headers=headers)#, proxies=proxies)#
    data_total = req.json()['subjects']
    time.sleep(4+random.random())
    # print(data_total)
    if not data_total:
        print('你搜索的不存在：', moviename)
        return

    for data in data_total:
        url_detail = data['alt']
        if douban_detail(url_detail):
            print('搜索到结果:', moviename)
            return data
    print('搜索结果中没有符合的条件：', moviename)


def douban_movies():
    client = pymongo.MongoClient()
    db = client.chinamovies
    collections = db.movies
    collections_detail = db.moviesdetail
    # db.drop_collection('movies')

    count = 0
    with open('notexistmovie.txt', 'r', encoding='utf-8') as f:
        movies = f.read().split()
    print(movies)

    for moviename in movies:
        with open('movieid.txt', 'r') as f:
            movieid = f.read().split()
        count += 1
        print(count)
        datadetail = douban_api(moviename)
        # print(datadetail)
        if datadetail:
            if str(datadetail['id']) not in movieid:
                movieid.append(datadetail['id'])
                print('已存数据库：', datadetail['id'], datadetail['title'])
                collections_detail.insert_one(datadetail)
                with open('movieid.txt', 'a') as f2:
                    f2.write(' '+datadetail['id'])
            else:
                print('该电影已存在，id：', datadetail['id'], datadetail['title'])
        else:
            with open('notexistmovie222.txt', 'a', encoding='utf-8') as f3:
                f3.write(' '+moviename)
        print('========================================')

# 与 step1 代码基本一致，但在几个函数中加了 input，手动输入值，人工判断，用来寻找在 step1 中由于名称原因没有找到的电影
douban_movies()
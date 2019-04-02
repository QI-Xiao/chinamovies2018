import pymongo
import requests
from bs4 import BeautifulSoup
import time
import re
import random

# 进入豆瓣每一部电影的页面，通过其上映日期和名称判断是否是所要的电影
def douban_detail(url_detail):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    }
    req = requests.get(url_detail,headers=headers)# , proxies=proxies
    soup = BeautifulSoup(req.text, 'lxml')
    releasedate = soup.find("div",id="info").find("span",property="v:initialReleaseDate",content=re.compile("2018.*(中国大陆)"))
    name = soup.find("div", id="content").h1.find("span", property=True).string
    time.sleep(1.5+random.random())
    if releasedate:
        print(name, ': ', releasedate.string)
        return True
    print(name, ': 没有信息')

# 从豆瓣api中搜索输入的电影名称，通过 douban_detail 函数判断是否符合条件
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
        if data['title'] != moviename:
            print(data['title'], ': 没有信息')
        else:
            url_detail = data['alt']
            if douban_detail(url_detail):
                print('搜索到结果:', moviename)
                return data
    print('搜索结果中没有符合的条件：', moviename)

# 根据中国票房网得到的电影数据，从豆瓣中获得更详细的数据
def douban_movies():
    client = pymongo.MongoClient()
    db = client.chinamovies
    collections = db.movies
    collections_detail = db.moviesdetail
    # db.drop_collection('movies')

    count = 0
    for i in collections.find():
        with open('movieid.txt', 'r') as f:
            movieid = f.read().split()
        count += 1
        print(count)
        print(i['MovieName'])
        moviename = i['MovieName']
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
            with open('notexistmovie.txt', 'a', encoding='utf-8') as f3:
                f3.write(' '+i['MovieName'])
        print('========================================')

# douban_movies()
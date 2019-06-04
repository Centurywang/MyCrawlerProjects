from time import sleep
import redis
import re
import requests
import threading
import pymongo
from lxml import etree
from bs4 import BeautifulSoup

class SaveCitiao:
    '''从redis数据库获取url爬取信息并保存到mongodb数据库'''
    def __init__(self):
        # 初始化数据库
        self.r = redis.Redis(host='47.101.222.18',password='wangshiji',port=6379,decode_responses=True)
        # mongodb数据库配置
        self.mg = pymongo.MongoClient('mongodb://47.101.222.18:27017/')
        self.mydb = self.mg['baiducitiao']
        self.mycol = self.mydb['citiao']
        # 请求头信息
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
            'Host': 'baike.baidu.com',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'http://baike.baidu.com/renwu'
        }
    def get_proxy(self):
        '''获取代理'''
        r = requests.get('http://127.0.0.1:5000/get')
        proxy = BeautifulSoup(r.text, "lxml").get_text()
        proxies = {'https': proxy,'http:':proxy}
        return proxies

    def get_request_info(self,):
        '''获取url等数据信息(字典)
        描述：{name: 词条名, url: 词条url, title: 词条类型}
        '''
        try:
            item = eval(self.r.spop('baiducitiao_requests'))
            # 判断该词条是否已经爬取
            judge = self.r.sadd('citiao_requested',str(item))
            while judge == 0:  # 词条已爬取,重新获取词条
                print('词条已爬取,重新获取词条')
                item = eval(self.r.spop('baiducitiao_requests'))
                judge = self.r.sadd('citiao_requested', str(item))
            return item
        except Exception as e:
            print('获取词条失败',e)


    def get_html(self,url,data=None):
        '''获取xpath响应'''
        #proxy = self.get_proxy()
        #print(proxy)
        if data is not None:
            html = requests.get(url=url, headers=self.headers, data=data,proxies=None)
        else:
            html = requests.get(url=url, headers=self.headers,proxies=None)
        html.encoding='utf-8'
        return html.text

    def get_citiao_info(self,content):
        '''获取词条内信息
        1.获取url
        2.请求url获取response(xpath)响应
        3.请求url获取其它数据
        '''
        print(content)
        url = content['url']
        response = self.get_html(url=url,data=None)
        item = {}
        item['title'] = content['title']
        item['name'] = content['name']

        html = etree.HTML(response)
        try:
            id = html.xpath('//a[@class="lemma-discussion cmn-btn-hover-blue cmn-btn-28 j-discussion-link"]/@href')[0]
            id = id[id.find('Id') + 3:]
        except:
            id = re.findall('newLemmaId:.*?"(.*?)"',response)
            if len(id)>0:
                id = id[0]
        url = 'https://baike.baidu.com/api/wikiui/sharecounter?lemmaId={}&method=get'.format(id)
        response2 = eval(self.get_html(url=url))
        item['likeCount'] = response2['likeCount']
        item['shareCount'] = response2['shareCount']
        item['dateUpdate'] = html.xpath('//meta[@itemprop="dateUpdate"]/@content')
        if len(item['dateUpdate']) > 0:
            item['dateUpdate'] = item['dateUpdate'][0]
        id = re.findall('newLemmaIdEnc:"(.*?)"', response)
        if len(id) > 0:
           id = id[0]
        url = 'https://baike.baidu.com/api/lemmapv?id={}'.format(id)
        response3 = eval(self.get_html(url=url))
        item['visitCount'] = response3["pv"]
        item['changeCount'] = re.findall('<li>(.*?)<a href.*?>历史版本</a></li>',response)
        #

        if len(item['changeCount']) > 0:
            item['changeCount'] = item['changeCount'][0]
            item['changeCount'] = re.findall('\d+', item['changeCount'])[0]
        print(item)
        self.save_to_mongodb(data=item)

    def save_to_mongodb(self,data):
        '''将数据插入mongodb数据库'''
        self.mycol.insert_one(data)




    def run(self):
        '''
        1.获取url等数据信息
        2.解析数据
        :return:
        '''
        # 1.获取url等数据信息
        content = True
        try:
            while content is not None:
                content = self.get_request_info()
                # 2.解析数据
                self.get_citiao_info(content=content)
                #sleep(1)
        except:
            self.run()

if __name__ == '__main__':
    citiao = SaveCitiao()
    citiao.run()


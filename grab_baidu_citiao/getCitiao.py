import requests
from lxml import etree
import redis

class GetCitiao:
    '''爬取百度词条url队列并放入redis数据库'''
    def __init__(self):
        '''初始化'''
        # redis数据库
        self.r = redis.Redis(host='47.101.222.18',password='wangshiji',port=6379,decode_responses=True)
        # 请求头信息
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
            'Host': 'baike.baidu.com',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'http://baike.baidu.com/renwu'
        }
    def get_response(self,url,data=None):
        '''获取xpath响应'''
        if data is not None:
            html = requests.get(url=url, headers=self.headers, data=data)
        else:
            html = requests.get(url=url, headers=self.headers)
        html.encoding='utf-8'
        return html.text

    def get_citiao_classify(self):
        '''获取词条分类及url'''
        index_url = 'https://baike.baidu.com/'
        response = self.get_response(url=index_url)
        response = etree.HTML(response)
        column_content = response.xpath('//div[@id="commonCategories"]//dl')
        results = []  # 保存所有词条分类及url
        for dl in column_content:
            item = {}
            item['title'] = dl.xpath('.//dd//a/text()')
            item['href'] = ['http://baike.baidu.com' + i for i in dl.xpath('.//dd//a/@href')]
            for title,href in zip(item['title'],item['href']):
                meta = {'title':title,'url':href}
                results.append(meta)
        print(results)
        return results

    def get_page_citiao(self,title,url):
        '''获取该页所有词条信息并存入redis数据库'''
        response = self.get_response(url=url)
        response = etree.HTML(response)
        column_content = response.xpath('//div[@class="grid-list grid-list-spot"]//ul//li')
        for li in column_content:
            item = {}
            item['title'] = title
            item['name'] = li.xpath('./div[@class="photo"]/a/@title')[0]
            item['url'] = 'http://baike.baidu.com' + li.xpath('./div[@class="photo"]/a/@href')[0]
            print(item)
            # 存入redis数据库
            self.r.sadd('baiducitiao_requests', str(item))

        # 如果该分类词条存在下一页
        next_page_url = response.xpath('//a[text()="下一页>"]/@href')
        if len(next_page_url) > 0:
            next_page_url = 'http://baike.baidu.com/fenlei/' + next_page_url[0]
            return next_page_url
        else:
            return None

    def run(self):
        '''
        1.获取词条分类
        2.进入分类，获取所有词条信息
        3.将词条信息放入redis数据库
        '''
        # 获取词条分类
        citiaoClassify = self.get_citiao_classify()
        # 获取所有词条信息
        for classify in citiaoClassify:
            nextPageUrl = self.get_page_citiao(title=classify['title'],url=classify['url'])
            while nextPageUrl is not None:
                print(nextPageUrl)
                nextPageUrl = self.get_page_citiao(title=classify['title'], url=nextPageUrl)

if __name__ == '__main__':
    getcitiao = GetCitiao()
    getcitiao.run()
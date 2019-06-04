import requests
import scrapy
from baiducitiao.pipelines import r
import re


class GetCiTiao(scrapy.Spider):
    name = 'downcitiao'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Host': 'baike.baidu.com',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://baike.baidu.com/renwu'
    }
    start_urls = []
    def start_requests(self):
        url = 1
        # item = eval(r.spop('citiaoRequests'))
        # url = item['url']
        # yield scrapy.Request(url=url, callback=self.parse, meta=item)
        while url is not None:
            item = eval(r.spop('citiaoRequests'))
            url = item['url']
            yield scrapy.Request(url=url,callback=self.parse,headers=self.headers,meta=item)
    def parse(self, response):
        item = {}
        item['title'] = response.meta['title']
        item['name'] = response.meta['name']
        id = response.xpath('//a[@class="lemma-discussion cmn-btn-hover-blue cmn-btn-28 j-discussion-link"]/@href').extract_first()
        if id is None:
            id = response.xpath('//a[@rel="nofollow"]/@href').extract_first()
            id = re.findall('/reference/(.*?)/',id)[0]
        id = id[id.find('Id')+3:]
        url = 'https://baike.baidu.com/api/wikiui/sharecounter?lemmaId={}&method=get'.format(id)
        data = {
            'lemmaId': id,
            'method': 'get'
        }
        response2 = requests.get(url=url,
                     allow_redirects=False, headers=self.headers, data=data)
        response2 = scrapy.FormRequest(
                        url=url,
                        method='GET'
                    )
        response2 = eval(response2.text)
        item['likeCount'] = response2['likeCount']
        item['shareCount'] = response2['shareCount']
        item['dateUpdate'] = response.xpath('//meta[@itemprop="dateUpdate"]/@content').extract_first()
        id = re.findall('newLemmaIdEnc:"(.*?)"',response.text)[0]
        url = 'https://baike.baidu.com/api/lemmapv?id={}'.format(id)
        data = {
            'id': id,
        }
        response3 = requests.get(url=url,
                                 allow_redirects=False, headers=self.headers, data=data)
        response3 = eval(response3.text)
        item['visitCount'] = response3["pv"]
        item['changeCount'] = response.xpath('//li[a[@class="nslog:1021"]/text()="历史版本"]/text()').extract_first()
        yield item
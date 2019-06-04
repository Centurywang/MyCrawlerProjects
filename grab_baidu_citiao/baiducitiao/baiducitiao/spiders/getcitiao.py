import scrapy



class GetCiTiao(scrapy.Spider):
    name = 'citiao'
    start_urls = ['https://baike.baidu.com/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Host': 'baike.baidu.com',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://baike.baidu.com/renwu'
    }
    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0],callback=self.parse,headers=self.headers)

    def parse(self, response):
        '''获取词条分类'''
        column_content = response.xpath('//div[@id="commonCategories"]//dl')
        for dl in column_content:
            item = {}
            item['title'] = dl.xpath('.//dd//a/text()').extract()
            item['href'] = ['http://baike.baidu.com'+i for i in dl.xpath('.//dd//a/@href').extract()]
            for title,href in zip(item['title'],item['href']):
                meta = {'title':title}
                yield scrapy.Request(url=href,callback=self.parse_citiao,meta=meta,headers=self.headers)


    def parse_citiao(self,response):
        '''获取分类内所有词条'''
        column_content = response.xpath('//div[@class="grid-list grid-list-spot"]//ul//li')
        for li in column_content:
            item = {}
            item['title'] = response.meta['title']
            item['name'] = li.xpath('./div[@class="photo"]/a/@title').extract_first()
            item['url'] = 'http://baike.baidu.com' + li.xpath('./div[@class="photo"]/a/@href').extract_first()
            yield item
        next_page_url = response.xpath('//a[text()="下一页>"]/@href').extract_first()
        if next_page_url is not None:
            next_page_url = 'http://baike.baidu.com/fenlei/' +  next_page_url
            scrapy.Request(url=next_page_url,callback=self.parse_citiao,meta=response.meta,headers=self.headers)

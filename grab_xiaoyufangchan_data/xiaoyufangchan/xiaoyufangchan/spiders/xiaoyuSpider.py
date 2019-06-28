import scrapy

class XiaoyuSpider(scrapy.Spider):
    name = 'xiaoyu'

    urls = [
        'http://fangzi.xmfish.com/web/search_hire.html?h=&hf=&ca=59201&r=&s=&a=&rm=&f=&d=&tp=&l=0&tg=&hw=&o=&ot=1&tst=0&page={}',
        'http://fangzi.xmfish.com/web/search_hire.html?h=&hf=&ca=59202&r=&s=&a=&rm=&f=&d=&tp=&l=0&tg=&hw=&o=&ot=0&tst=0&page={}',
        'http://fangzi.xmfish.com/web/search_hire.html?h=&hf=&ca=59203&r=&s=&a=&rm=&f=&d=&tp=&l=0&tg=&hw=&o=&ot=1&tst=0&page={}',
        'http://fangzi.xmfish.com/web/search_hire.html?h=&hf=&ca=59204&r=&s=&a=&rm=&f=&d=&tp=&l=0&tg=&hw=&o=&ot=0&tst=0&page={}',
        'http://fangzi.xmfish.com/web/search_hire.html?h=&hf=&ca=59205&r=&s=&a=&rm=&f=&d=&tp=&l=0&tg=&hw=&o=&ot=1&tst=0&page={}',
        'http://fangzi.xmfish.com/web/search_hire.html?h=&hf=&ca=59206&r=&s=&a=&rm=&f=&d=&tp=&l=0&tg=&hw=&o=&ot=0&tst=0&page={}',
        'http://fangzi.xmfish.com/web/search_hire.html?h=&hf=&ca=59207&r=&s=&a=&rm=&f=&d=&tp=&l=0&tg=&hw=&o=&ot=1&tst=0&page={}',
        'http://fangzi.xmfish.com/web/search_hire.html?h=&hf=&ca=59208&r=&s=&a=&rm=&f=&d=&tp=&l=0&tg=&hw=&o=&ot=0&tst=0&page={}'
    ]
    start_urls = [
        urls[0].format(1),
        urls[1].format(1),
        urls[2].format(1),
        urls[3].format(1),
        urls[4].format(1),
        urls[5].format(1),
        urls[6].format(1),
        urls[7].format(1),
    ]
    def parse(self,response):
        content = response.xpath('//ul[@class="section-fy-list"]//li')
        for con in content:
            item = {}
            item['title'] = con.xpath('./div[@class="list-img"]//img/@title').extract_first()
            item['describe'] = con.xpath('.//span[@class="list-attr"]//em/text()').extract()
            item['address'] = con.xpath('.//span[@class="list-addr"]//em[2]/a/text()').extract_first()
            item['address_first'] = con.xpath('.//span[@class="list-addr"]//em[1]/a/text()').extract_first()
            item['address_second'] = '-'.join(con.xpath('.//span[@class="list-addr"]//em[2]/a/text()').extract())
            item['sale_source'] = con.xpath('.//div[@class="list-agency"]/span/i/text()').extract_first().replace('：','').strip()
            item['sale_person'] = con.xpath('.//div[@class="list-agency"]/span/text()').extract_first().strip()
            item['feature'] = con.xpath('.//div[@class="list-agency"]//a/em/text()').extract()
            item['release_date'] = con.xpath('.//span[contains(text(),"最近更新")]/text()').extract_first().replace('最近更新：','')
            item['price'] = con.xpath('.//span[@class="list-price"]/b/text()').extract_first()
            yield item

        next_page_url = response.xpath('//a[text()="下一页"]/@href').extract_first()
        if next_page_url is not None:
            next_page_url = 'http://fangzi.xmfish.com' + next_page_url
            yield scrapy.Request(next_page_url,callback=self.parse)
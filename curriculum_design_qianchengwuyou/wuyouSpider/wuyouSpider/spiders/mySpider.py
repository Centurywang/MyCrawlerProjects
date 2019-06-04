import scrapy

# count用于统计页数，在测试时控制爬取的页面数
# count = 1


class MySpider(scrapy.Spider):
    name = 'wuyou'
    index_url = 'https://search.51job.com/list/000000,000000,0000,00,9,99,%25E5%25A4%25A7%25E6%2595%25B0%25E6%258D%25AE,2,{}.html'
    start_urls = [
        index_url.format(1)
    ]

    def parse(self,response):
        '''获取一级页面数据'''
        content = response.xpath("//div[@class='dw_table']//div[@class='el']")
        for con in content:
            item = {}
            item['work_name'] = con.xpath('./p/span/a/@title').extract_first()
            href = con.xpath('./p/span/a/@href').extract_first()
            item['company_name'] = con.xpath('./span[@class="t2"]/a/@title').extract_first()
            item['work_location'] = con.xpath('./span[@class="t3"]/text()').extract_first()
            item['work_salary'] = con.xpath('./span[@class="t4"]/text()').extract_first()
            item['release_date'] = con.xpath('./span[@class="t5"]/text()').extract_first()
            meta = item
            yield scrapy.Request(href,callback=self.parse_work_info,meta=meta)
        # 获取下一页
        next_page_url = response.xpath('//a[text()="下一页"]/@href').extract_first()
        if next_page_url is not None:
            print(next_page_url)
            # count用于统计页数，在测试时控制爬取的页面数
            # global count
            # count += 1
            # if count > 3: # 爬取大于第三页时退出
            #     return False
            yield scrapy.Request(next_page_url,callback=self.parse)


    def parse_work_info(self,response):
        '''获取二级页面数据'''
        item = response.meta
        # 结果为一串字符，需要进行分割 并去除空字符
        content1 = response.xpath("//div[@class='in']/div[@class='cn']/p[@class='msg ltype']/@title").extract_first().split('|')
        content1 = [i.strip() for i in content1]
        # 提取结果 ['广州-天河区', '5-7年经验', '本科', '招1人', '06-03发布']
        for con in content1:
            if con in ['初中及以下', '高中/中技/中专', '本科', '无工作经验', ' 大专']:
                item['edu_level'] = con
            if con.find('招') != -1:
                item['work_require_people'] = con
            if con.find('经验') != -1:
                item['work_exp'] = con
        for column in ['edu_level', 'work_require_people', 'work_exp', 'release_time']:
            if column not in item.keys():
                item[column] = None
        # 公司性质  公司规模（人数）  公司所属行业
        item['company_type'] = response.xpath("//div[@class='com_tag']/p[1]/@title").extract_first()
        item['company_size'] = response.xpath("//div[@class='com_tag']/p[2]/@title").extract_first()
        item['company_industry'] = response.xpath("//div[@class='com_tag']/p[3]/@title").extract_first().replace(',', ' ')
        yield item
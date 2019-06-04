import io
import sys
from lxml import etree
import requests

class WuyouSpider:
    def __init__(self):
        self.headers = {
            'Host': 'search.51job.com',
            'Referer': '{}',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        }
        self.url = 'https://search.51job.com/list/120200,000000,0000,00,9,99,%25E5%25A4%25A7%25E6%2595%25B0%25E6%258D%25AE,2,{}.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
        self.file = open('big_data.json','w')

    def get_response(self,url,headers=None):
        '''返回response'''
        response = requests.get(url,headers=headers)
        #response.encoding = 'utf-8'
        response.encoding = 'gbk'
        return response.text

    def parse_data(self,data):
        '''处理xpath结果 将列表去除'''
        return ''.join(data)
    def parse_info(self,url):
        '''获取职位信息'''
        response = self.get_response(url,headers=self.headers)
        html_content = etree.HTML(response)
        info = {}
        info['job_name'] = self.parse_data(html_content.xpath("//div[@class='in']//h1/@title"))
        info['company_name'] = self.parse_data(html_content.xpath("//div[@class='in']//a[@class='catn']/@title"))
        info['salary'] = self.parse_data(html_content.xpath("//div[@class='cn']//strong/text()"))
        content1 = self.parse_data(html_content.xpath("//div[@class='cn']//p[@class='msg ltype']/@title")).split('|')
        content1 = [i.strip() for i in content1]
        info['work_city'] = content1[0]
        info['work_exp'] = content1[1]
        info['require_people'] = content1[2]
        info['date'] = content1[3]
        info['require_skill'] = self.parse_data(html_content.xpath('//div[@class="bmsg job_msg inbox"]//text()')).strip().replace('\t','').replace('\n','').replace('\r','')
        info['job_name'] = self.parse_data(html_content.xpath("//div[@class='in']//h1/@title"))
        self.file.write(str(info)+'\n')
        print(info)

    def parse_page(self):
        '''获取职位链接'''
        # 1.获取首页职位链接
        href = [1,2,3,4,5]
        page = 1
        while len(href)>4:
            start_url = self.url.format(page)
            self.headers['Referer'] = start_url
            response = self.get_response(start_url,headers=self.headers)
            html_content = etree.HTML(response)
            href = html_content.xpath("//div[@class='el']/p//a/@href")
            for url in href:
                try:
                    self.parse_info(url)
                except Exception as e:
                    print(e)
            page += 1



    def run(self):
        '''爬取前程无忧大数据职位信息
        1.获取首页职位链接
        2.根据职位链接获取职位信息 并写入文件
        3.获取下一页职位链接
        4.根据职位链接获取职位信息 并写入文件
        5.判断下一页数据是否为空，空则退出爬虫
        '''
        self.parse_page()
        self.file.close()

if __name__ == '__main__':
    qiancheng = WuyouSpider()
    qiancheng.run()

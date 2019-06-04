import requests
from lxml import etree
import json
from controlMGDB import Control_MGDB
from conDB import ConDB


def get_response(url):
    '''获取response响应'''
    response = requests.get(url)
    response.encoding='gbk'
    return response.text

def parse_page(response):
    '''解析网页，获取职位名，公司名，工作地点，薪资和发布时间'''
    # 保存该页所有职位信息
    page_works_info = []
    html = etree.HTML(response)
    # 岗位数据保存在网页内的 class="el" 的div标签下
    work_contents = html.xpath('//div[@class="el"]')
    for content in work_contents[4:]:
        # work_info 保存职位信息
        work_info = {}
        # 获取职位名 职位名 在 第一个p标签下的span标签下的a标签的title属性
        work_info['name'] = content.xpath('.//p/span/a/@title')[0]
        # 获取公司名 class="t2"的span标签下的a标签的title属性
        work_info['company'] = content.xpath('.//span[@class="t2"]/a/@title')[0]
        # 获取工作地点 class="t3"的span下的text()属性
        work_info['city'] = content.xpath('.//span[@class="t3"]/text()')[0]
        # 获取工作薪资 class="t4"的span下的text()属性
        # 工作薪资可能为空 空的话 填入 "空"
        work_info['salary'] = content.xpath('.//span[@class="t4"]/text()')
        if len(work_info['salary']) < 1:
            work_info['salary'] = '空'
        else:
            work_info['salary'] = content.xpath('.//span[@class="t4"]/text()')[0]
        # 获取工作发布时间 class="t5"的span下的text()属性
        work_info['date'] = content.xpath('.//span[@class="t5"]/text()')[0]
        print(work_info)
        page_works_info.append(work_info)
    print(len(page_works_info))
    return page_works_info

def get_next_page_url(response):
    '''获取下一页url地址'''
    html = etree.HTML(response)
    # 下一页url在 text()属性为"下一页"的a标签下的href属性
    next_page_url = html.xpath('//a[text()="下一页"]/@href')
    print(next_page_url)
    if len(next_page_url) > 0:
        return next_page_url[0]
    else:
        return False

def save_to_json(filename,data):
    '''保存数据到json文件'''
    filename = filename+'.json'
    data = json.dumps(data)
    print('正在保存%s'%filename)
    with open(filename,'w') as f:
        f.write(data)
    print('保存完成')


def run():
    '''爬虫
    从“前程无忧”网站中搜索济南的大数据相关岗位
    收集职位名，公司名，工作地点，薪资和发布时间
    1.获取首页response响应
    2.解析网页数据，获取职位名，公司名，工作地点，薪资和发布时间
    3.循环获取下一页
        获取response响应
        解析网页数据，获取职位名，公司名，工作地点，薪资和发布时间
    4.先保存到json文件内
    '''
    index_url = 'https://search.51job.com/list/120200,000000,0000,00,9,99,%25E5%25A4%25A7%25E6%2595%25B0%25E6%258D%25AE,2,1.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
    # 保存所有数据
    works_info_result = []
    # 获取首页response响应
    response = get_response(index_url)
    # 解析网页数据，获取职位名，公司名，工作地点，薪资和发布时间
    works_info_result.extend(parse_page(response))
    # 获取下一页
    next_page_url = get_next_page_url(response)
    while next_page_url:
        # 获取response响应
        response = get_response(next_page_url)
        # 解析网页数据，获取职位名，公司名，工作地点，薪资和发布时间
        works_info_result.extend(parse_page(response))
        # 获取下一页
        next_page_url = get_next_page_url(response)
    print('爬取完成')
    # 将数据保存到json文件
    save_to_json(filename='JNworks.json',data=works_info_result)
    # 构造数据库对象（Mongodb）
    mgdb = Control_MGDB('mongodb://localhost:27017/')
    # 构造数据库对象（Mysql）
    mydb = ConDB(ip=None,username=None,password=None)
    # 将数据插入数据库(mysql)
    for data in works_info_result:
        # 将字典中的值提取
        data = list(data.values())
        # 根据数据构造sql语句
        sql = 'insert into jinanworks values("{}","{}","{}","{}","{}")'.format(data[0],data[1],data[2],data[3],data[4])
        print(sql)
        # 执行sql语句
        mydb.execute_sql(sql)

    print(works_info_result)
    print(len(works_info_result))
    # 执行插入操作(Mongodb)
    print(len(mgdb.insert_documents(db_name='Works',sets_name='bigdata_works',data=works_info_result)))


if __name__ == '__main__':
    run()
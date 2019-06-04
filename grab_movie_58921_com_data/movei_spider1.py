from lxml import etree
import requests

def get_response(url):
    '''
    获取url的response
    :param url:
    :return:
    '''
    return requests.get(url)

def xpath_search(xpath_grammer,response):
    '''
    根据xpath语法对response进行查找
    :param xpath_grammer:
    :param response:
    :return:
    '''
    html = etree.HTML(response.text)
    result = html.xpath(xpath_grammer)
    return result

def main():
    '''
    从电影票房数据库http://58921.com/ 中提取：概况表格中的电影名称，当日排片，当日人次，当日预售票房，实时累积票房。
    分析页面得 概况表格在class属性为"table table table-bordered table-condensed"的table标签下
    每一个tr标签包含一行数据
    '''
    url = 'http://58921.com/'
    response = get_response(url)
    # 设置格式
    response.encoding='utf-8'
    # 获取表格内容 语句解析：查询网页源码中所有class属性为"table table table-bordered table-condensed"的所有table标签的内容
    xpath_grammer1 ='//table[@class ="table table table-bordered table-condensed"]/tbody//tr'
    table_content = xpath_search(xpath_grammer1,response)
    # 根据table标签
    # table_content索引为:-1是因为最后一个tr标签内的是票房仅供参考
    for movie_info in table_content[:-1]:
        movie = {}
        # xpath语句解析： 该节点下第一个td标签文本内容
        movie['电影名称'] = movie_info.xpath('.//td[1]//text()')
        movie['当日排片'] = movie_info.xpath('.//td[2]//text()')
        movie['当日排片'] = movie['当日排片'][0] if len(movie['当日排片']) > 0 else movie['当日排片']
        movie['当日人次'] = movie_info.xpath('.//td[3]//text()')
        movie['当日预售票房'] = movie_info.xpath('.//td[4]//text()')
        movie['实时累计票房'] = movie_info.xpath('.//td[5]//text()')
        print(movie)

if __name__ == '__main__':
    main()
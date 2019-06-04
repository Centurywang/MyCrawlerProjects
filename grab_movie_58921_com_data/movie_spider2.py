import requests
from lxml import etree
import ConnectMySql

def get_response(url):
    '''
    根据url添加headers请求头获取response
    :param url:
    :return:response
    '''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    }
    return requests.get(url,headers=headers)

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
    从https://movie.douban.com/top250豆瓣电影Top250第一页中提取：排名；电影名称；评分；评价人数；引用语
    （*）导演；主演；年份  国家  类型
    分析页面得 电影信息在class="grid_view"的ol标签下 每个li里包含一个电影信息
    :return:
    '''
    url = 'https://movie.douban.com/top250'
    response = get_response(url)
    # 获取每个电影信息
    xpath_grammer = '//ol[@class="grid_view"]//li'
    movies_info = xpath_search(xpath_grammer,response)
    movies = []
    # 实例化mysql操作类
    mysql = ConnectMySql.MySQLDB()

    for movie_info in movies_info:

        movie = {}
        # 排名在class属性为hd的div标签下的a标签的第一个span标签的文本
        movie['排名'] = movie_info.xpath('.//div[@class="pic"]/em/text()')[0]
        movie['电影名称'] = movie_info.xpath('.//div[@class="hd"]/a/span[1]/text()')[0]
        movie['评分'] = movie_info.xpath('.//span[@class="rating_num"]/text()')[0]
        movie['评价人数'] = movie_info.xpath('.//div[@class="star"]/span[4]/text()')[0]
        movie['引用语'] = movie_info.xpath('.//span[@class="inq"]/text()')[0]
        movies .append(movie)

    print(movies)
        # 根据信息构造sql语句
        # sql = 'insert into doubanMovieInfo values("{}","{}","{}","{}","{}")'.format(movie['排名'],movie['电影名称'],movie['评分'],movie['评价人数'],movie['引用语'])
        # #print(sql)
        # # 执行sql语句
        # mysql.execute_update(sql)
    # print(len(moveis))
    #return movies





if __name__ == '__main__':
    main()
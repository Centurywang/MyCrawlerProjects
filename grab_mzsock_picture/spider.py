import os
import requests
from lxml import etree

start_urls = [
    {'name': '棉袜', 'url': 'http://mzsock.com/mv/'},
    {'name': '船袜', 'url': 'http://mzsock.com/cy/'},
    {'name': '丝袜', 'url': 'http://mzsock.com/sw/'},
    {'name': '裸足', 'url': 'http://mzsock.com/lz/'},
    {'name': '帆布鞋', 'url': 'http://mzsock.com/fbx/'},
    {'name': '运动鞋', 'url': 'http://mzsock.com/ydx/'},
    {'name': '人字拖', 'url': 'http://mzsock.com/rzt/'},
    {'name': '自拍', 'url': 'http://mzsock.com/cwzp/'}
]

def get_response(url):
    response = requests.get(url)
    return response.text

def extract_list_data(data):
    '''提取列表中第一个数据 若列表数据不足一 则返回None'''
    judge = len(data)
    return data[0] if judge else None

def get_img_num(url):
    '''获取套图总数'''
    response = get_response(url)
    response = etree.HTML(response)
    img_num = extract_list_data(response.xpath('//span[@class="more r"]/em/text()'))
    return img_num

def download_picture(name,url):
    '''下载图片'''
    img_content = requests.get(url).content
    with open(name,'wb') as f:
        f.write(img_content)

def create_dictionary(name):
    '''创建文件夹'''
    try:
        os.mkdir(name)
    except Exception as e:
        print(e)

def judge_file_exists(name):
    '''判断文件是否存在'''
    try:
        with open(name) as f:
            return True
    except Exception as e:
        return False

def get_img(name,url):
    '''获取图片'''
    response = get_response(url)
    response = etree.HTML(response)
    max_page = extract_list_data(response.xpath('//a[@title="最后页"]/text()'))    # 获取最大页
    if max_page is not None:
        max_page = int(max_page)
    else:
        return None
    create_dictionary(name)  # 创建文件夹
    # 构造url
    for page in range(1,max_page+1):
        page_url = url[:-5]+'_{}'.format(page)+url[-5:]
        response = get_response(page_url)
        response = etree.HTML(response)
        img_srcs = response.xpath('//div[@class="picsbox picsboxcenter chenxing_pic_images"]//img/@src')
        for src in img_srcs:
            judge = judge_file_exists(name+'/'+src.split('/')[-1])
            if judge is False:
                download_picture(name=name+'/'+src.split('/')[-1],url=src)  # 保存

def get_type_imgs(name,url):
    '''获取一个分类下所有页面套图信息'''
    # 获取套图总数  因为一页为20张套图
    page_num = int(get_img_num(url))
    # 所以页数为 套图总数/20 + 1(原因：int整形数据除数会消掉小数点后的数)
    page_num = int(page_num/20) +1
    create_dictionary(name) # 创建文件夹
    for page in range(1,page_num+1):
        page_url = url+'page/{}/'.format(page)
        page_imgs = get_page_imgs(page_url) # 获取该页所有套图信息(名称与链接)
        for img in page_imgs:
            print('正在爬取{}-{}'.format(name,img['name']))
            get_img(name=name+'/'+img['name'],url=img['href'])
            print('爬取完成{}-{}'.format(name, img['name']))


def get_page_imgs(url):
    '''获取该页所有套图信息'''
    page_imgs = []
    response = get_response(url)
    response = etree.HTML(response)
    content = response.xpath('//ul[@class="post-list cl"]//li/h3[@class="post-title"]')
    for con in content:
        name = extract_list_data(con.xpath('./a/@title'))
        href = extract_list_data(con.xpath('./a/@href'))
        page_imgs.append({'name':name,'href':href})
    return page_imgs

def main():
    # 选择类型
    choice = input('请选择要抓取的类型:\n1.棉袜2.船袜3.丝袜4.裸足5.帆布鞋6.运动鞋7.人字拖8.自拍0.退出程序\n请选择:')
    while True:
        if choice == 0:
            print('程序退出')
            break
        elif choice in [str(i) for i in range(1,9)]:
            choice = int(choice) - 1
            get_type_imgs(start_urls[choice]['name'], start_urls[choice]['url'])
        else:
            print('请重新输入')


if __name__ == '__main__':
    main()

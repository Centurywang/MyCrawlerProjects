import requests
from bs4 import BeautifulSoup

def get_proxy():
    r = requests.get('http://127.0.0.1:5000/get')
    proxy = BeautifulSoup(r.text, "lxml").get_text()
    proxy = 'http://'+proxy
    return proxy


if __name__ == '__main__':
    proxies = get_proxy()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'Host': 'baike.baidu.com',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'http://baike.baidu.com/renwu'
    }
    print(proxies)
    #response = requests.get(url='https://baike.baidu.com/item/%E7%88%B1%E5%BD%BC/1490155?fromtitle=%E7%88%B1%E5%BD%BC%E8%A1%A8&fromid=2834580',headers=headers,proxies=proxies)
    #response.encoding='utf-8'
    #print(response.text)
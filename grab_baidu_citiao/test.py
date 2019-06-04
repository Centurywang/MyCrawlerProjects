import requests
from lxml import etree


url = 'https://baike.baidu.com/item/%E5%9C%86%E8%B6%B3%E5%B8%83'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Host': 'baike.baidu.com',
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'https://baike.baidu.com/item/%E5%9C%86%E8%B6%B3%E5%B8%83'
}


response = requests.get(url,allow_redirects=False,headers=headers)
response.encoding='utf-8'
html = etree.HTML(response.text)
id = html.xpath('//a[@class="lemma-discussion cmn-btn-hover-blue cmn-btn-28 j-discussion-link"]/@href')[0]
print('/planet/talk?lemmaId=3070959'.find('Id'))
print(id[21:])

print()
data = {
    'lemmaId': id[21:],
    'method': 'get'
}
print(data)
response = requests.get(url='https://baike.baidu.com/api/wikiui/sharecounter?lemmaId=3070959&method=get',allow_redirects=False,headers=headers,data=data)
print(response.text)
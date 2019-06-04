import json
from threading import Thread
import pymongo
import re
from time import sleep
import requests
from lxml import etree

class XieChenSpider:
    '''爬取携程酒店山东数据'''
    def __init__(self):
        self.headers = {
            'referer': 'https://hotels.ctrip.com/jiudian/shandong',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
        }
        # mongodb数据库配置
        self.mg = pymongo.MongoClient('mongodb://47.101.222.18:27017/')
        self.mydb = self.mg['xiecheng']

    def get_page_count(self,url):
        '''获取页数'''
        response = requests.get(url,headers=self.headers)
        html = etree.HTML(response.text)
        page_count = html.xpath('//a[@rel="nofollow" and @data-type="page"]/text()')
        if len(page_count)>0:
            return int(page_count[0])
        else:
            return None

    def get_one_page_data(self,page,city_data):
        post_url = 'https://hotels.ctrip.com/Domestic/Tool/AjaxHotelList.aspx'
        data = {
        '__VIEWSTATEGENERATOR': 'DB1FBB6D','cityName': city_data['cityName'],'StartTime': '2019-05-14','DepTime': '2019-05-15','RoomGuestCount': '1,1,0',
        'txtkeyword':'','Resource':'', 'Room':'', 'Paymentterm':'', 'BRev':'',
        'Minstate':'', 'PromoteType':'', 'PromoteDate':'', 'NEWHOTELORDER': 'NEWHOTELORDER','PromoteStartDate':'',
        'PromoteEndDate':'', 'OrderID':'',  'RoomNum':'', 'IsOnlyAirHotel': 'F','cityId': city_data['cityId'],'cityPY': city_data['cityPY'],'cityCode': city_data['cityCode'],
        'cityLat': city_data['cityLat'],'cityLng': city_data['cityLng'],'positionArea':'',
        'positionId':'','hotelposition':'', 'keyword':'', 'hotelId':'',
        'htlPageView': 0,'hotelType': 'F','hasPKGHotel': 'F','requestTravelMoney': 'F',
        'isusergiftcard': 'F','useFG': 'F','HotelEquipment':'','priceRange': -2,
        'hotelBrandId':'', 'promotion': 'F','prepay': 'F','IsCanReserve': 'F',
        'OrderBy': 99,'OrderType':'', 'k1':'','k2':'', 'CorpPayType':'', 'viewType':'',  'checkIn': '2019-05-14',
        'checkOut': '2019-05-15',    'DealSale':'', 'ulogin':'',  'hidTestLat': '0%7C0',
        'AllHotelIds': city_data['AllHotelIds'],
        'psid':'',  'isfromlist': 'T', 'ubt_price_key': 'htl_search_result_promotion','showwindow':'', 'defaultcoupon':'', 'isHuaZhu': 'False',
        'hotelPriceLow':'', 'unBookHotelTraceCode':'',  'showTipFlg':'',   'traceAdContextId': 'v2_H4sIAAAAAAAAAEXLvQ3CMBCG4dAxAyVKhTjJd74%2Fp2SRyHbimg2QmIA5YAsmI0qk0H3S873H1%2FP7%2FsDpEUndx3qvI1GIMSQdcUDmK5IQyyoRWVQw7IISdWvEmJXTv0khroJMTmFPkFTSBkTLjrzJubv0Rq2hcIXJPQOnZOCqBPNkPGcvxQqGw9C3Kq14drDWll%2BtBsXIAXNC0zgLerl1P92J9b7aAAAA',
        'allianceid': 0,  'sid': 0, 'pyramidHotels': city_data['pyramidHotels'],
        'hotelIds': city_data['hotelIds'],
        'markType': 0, 'zone':'',  'location':'',  'type':'', 'brand':'', 'group':'',   'feature':'',
        'equip':'',  'bed':'',  'breakfast':'',  'other':'', 'star':'','sl':'', 's':'','l':'',  'price':'',
        'a': 0, 'keywordLat':'', 'keywordLon':'', 'contrast': 0, 'PaymentType':'', 'CtripService':'', 'promotionf':'',
        'allpoint':'', 'page': page, 'contyped': 0, 'productcode':''
    }
        response = requests.post(post_url,data=data,headers=self.headers)
        content = json.loads(response.text)

        data = content['hotelPositionJSON']
        result = []
        for d in data:
            # 字段：酒店名:hotel_name 酒店星级:hotel_level 酒店地点:hotel_location
            # 酒店评分:hotel_score 推荐比例:recommendation_rate 评论人数:score_count  酒店价格:hotel_price 酒店房间数量:room_count
            hotel = {}
            hotel['hotel_name'] = d['name']
            hotel['hotel_price'] = float(re.findall('"hotelid":"{}","amount":"(.*?)"'.format(d['id']),str(content))[0])
            hotel['hotel_location'] = d['address']
            hotel['hotel_city'] = city_data['cityPY']
            hotel['hotel_score'] = float(d['score'])
            hotel['recommendation_rate'] = d['dpscore']+'%'
            hotel['score_count'] = int(d['dpcount'])
            try:
                hotel['room_count'] = int(re.findall('(\d+)间房',requests.post('https://hotels.ctrip.com/'+d['url'],headers=self.headers).text)[0])
            except:
                hotel['room_count'] = None
            hotel_level = d['star']
            hotel['hotel_level'] = int(hotel_level[-1]) if len(hotel_level)>0 else None
            print(hotel)
            self.mycol = self.mydb[city_data['cityPY']]
            self.mycol.insert_one(hotel)
            result.append(hotel)
        return result

    # def save_to_json(self,city):
    #     '''保存到json文件'''
    #     data = [i for i in self.mycol.find({},{'_id':0})]
    #     data = json.dumps(data)
    #     with open('jinanHotel.json','w') as f:
    #         f.write(data)
    #
    # def save_to_csv(self,city):
    #     '''保存到csv文件'''
    #     mycol = self.mydb[city]
    #     data = [i for i in mycol.find({},{'_id':0})]
    #     columns = [i for i in data[0].keys()]
    #     print(columns)
    #     with open(city+'.csv','w',encoding='utf-8') as f:
    #         f.write(','.join(columns)+'\n')
    #         for i in data:
    #             print(i.values())
    #             f.write(','.join([str(z) for z in i.values()])+'\n')

    def thread_run(self,city_url,city_data):
        '''开启多线程'''
        pageCount = self.get_page_count(city_url)
        result = []
        for i in range(1, pageCount + 1):
            result.extend(self.get_one_page_data(i,city_data))
            sleep(2)



    def run(self):
        '''运行'''
        #测试，获取济南、青岛、济宁所有酒店数据
        jinan_url = 'https://hotels.ctrip.com/hotel/jinan144'
        qingdao_url = 'https://hotels.ctrip.com/hotel/qingdao7'
        jining_url = 'https://hotels.ctrip.com/hotel/jining318'
        # 各城市请求参数
        jinan_data = {
            'cityName': '%E6%B5%8E%E5%8D%97',
            'cityId': 144,
            'cityPY': 'jinan',
            'cityCode': '0531',
            'cityLat': 36.6575700112,
            'cityLng': 117.1263985183,
            'AllHotelIds':'668132%2C1618095%2C474168%2C661272%2C11446097%2C474446%2C474277%2C666884%2C474311%2C603246%2C22033096%2C481622%2C701356%2C33015637%2C23888279%2C1316978%2C6027289%2C638459%2C18518578%2C5099344%2C2619983%2C602672%2C6279766%2C848612%2C6170654',
            'pyramidHotels':'22033096_11%7C1316978_16',
            'hotelIds':'668132_1_1,1618095_2_1,474168_3_1,661272_4_1,11446097_5_1,474446_6_1,474277_7_1,666884_8_1,474311_9_1,603246_10_1,22033096_11_1,481622_12_1,701356_13_1,33015637_14_1,23888279_15_1,1316978_16_1,6027289_17_1,638459_18_1,18518578_19_1,5099344_20_1,2619983_21_1,602672_22_1,6279766_23_1,848612_24_1,6170654_25_1',
        }
        qingdao_data = {
            'cityName': '%E9%9D%92%E5%B2%9B',
            'cityId': 7,
            'cityPY': 'qingdao',
            'cityCode': '0532',
            'cityLat': 36.0732156758,
            'cityLng': 120.3890923844,
            'AllHotelIds': '21124467%2C654770%2C23472335%2C6508376%2C28761837%2C438037%2C5930359%2C483417%2C29715350%2C25270439%2C6838355%2C436468%2C2329361%2C4719799%2C669124%2C19438626%2C5264336%2C5214763%2C6074225%2C532185%2C24532652%2C486063%2C1371788%2C6273850%2C2359489',
            'pyramidHotels': '438037_6%7C6838355_11%7C19438626_16%7C24532652_21',
            'hotelIds': '21124467_1_1,654770_2_1,23472335_3_1,6508376_4_1,28761837_5_1,438037_6_1,5930359_7_1,483417_8_1,29715350_9_1,25270439_10_1,6838355_11_1,436468_12_1,2329361_13_1,4719799_14_1,669124_15_1,19438626_16_1,5264336_17_1,5214763_18_1,6074225_19_1,532185_20_1,24532652_21_1,486063_22_1,1371788_23_1,6273850_24_1,2359489_25_1',
        }
        jining_data = {
            'cityName': '%E6%B5%8E%E5%AE%81',
            'cityId': 318,
            'cityPY': 'jining',
            'cityCode': '0537',
            'cityLat': 35.4206614618,
            'cityLng': 116.5938941336,
            'AllHotelIds': '24054445%2C512863%2C669467%2C697554%2C755041%2C8425235%2C755051%2C2069861%2C1307747%2C35002191%2C5640860%2C25064588%2C474602%2C4687309%2C8498175%2C980063%2C33516324%2C1718572%2C756315%2C1816571%2C1861413%2C2302121%2C1359661%2C12598335%2C709377',
            'pyramidHotels': '5640860_11%7C980063_16%7C1861413_21',
            'hotelIds': '24054445_1_1,512863_2_1,669467_3_1,697554_4_1,755041_5_1,8425235_6_1,755051_7_1,2069861_8_1,1307747_9_1,35002191_10_1,5640860_11_1,25064588_12_1,474602_13_1,4687309_14_1,8498175_15_1,980063_16_1,33516324_17_1,1718572_18_1,756315_19_1,1816571_20_1,1861413_21_1,2302121_22_1,1359661_23_1,12598335_24_1,709377_25_1'
        }
        jinan_thread = Thread(target=self.thread_run,args=(jinan_url,jinan_data))
        qingdao_thread = Thread(target=self.thread_run,args=(qingdao_url,qingdao_data))
        jining_thread = Thread(target=self.thread_run,args=(jining_url,jining_data))
        #jinan_thread.start()
        qingdao_thread.start()
        #jining_thread.start()


if __name__ == '__main__':
    xiecheng = XieChenSpider()
    xiecheng.run()
    #xiecheng.save_to_csv(city='jinan')
    #xiecheng.save_to_json()
'''
    def get_page_hotel_data(self,html):
        #获取页面内酒店数据
        results = []
        data = html.xpath('//div[@id="hotel_list"]//div[@class="hotel_new_list J_HotelListBaseCell"]')
        for d in data:
            # 字段：酒店名:hotel_name 酒店星级:hotel_level 酒店地点:hotel_location
            # 酒店标签:hotel_tag 酒店评分:hotel_score 推荐比例:recommendation_rate 评论人数:score_count 评论标签:comment_tag 酒店价格:hotel_price
            hotel = {}
            hotel['hotel_name'] = d.xpath('.//li[@class="hotel_item_name"]//h2[1]/a/@title')[0]
            hotel['hotel_level'] = d.xpath('.//li[@class="hotel_item_name"]//span[contains(@class,"hotel_")]/@class')[-1][-1]
            hotel['hotel_level_name'] = d.xpath('.//li[@class="hotel_item_name"]//span[contains(@class,"hotel_")]/@title')[-1]
            hotel['hotel_location'] = d.xpath('.//p[@class="hotel_item_htladdress"]/text()')[-1][1:]
            hotel['hotel_tag'] = ','.join(d.xpath('.//li[@class="hotel_item_name"]//span[@class="special_label"]//text()'))
            hotel['hotel_score'] = d.xpath('.//span[@class="hotel_value"]/text()')[0]
            hotel['recommendation_rate'] = d.xpath('.//span[@class="total_judgement_score"]/span/text()')[0]
            hotel['score_count'] = d.xpath('.//span[@class="hotel_judgement"]/span/text()')[0]
            hotel['comment_tag'] = ','.join(d.xpath('.//span[@class="recommend"]//text()'))
            hotel['hotel_price'] = d.xpath('.//span[@class="J_price_lowList"]/text()')[0]
            results.append(hotel)
        return results


    def get_all_pages_data(self):
        #获取所有页面下酒店数据
        response = requests.get(url='https://hotels.ctrip.com/hotel/qingdao7', headers=self.headers)
        data = []
        html = etree.HTML(response.text)
        data.extend(self.get_page_hotel_data(html))
        next_page_url = html.xpath('//a[text()="下一页"]/@href')
        print(data)
        print(next_page_url)
    '''
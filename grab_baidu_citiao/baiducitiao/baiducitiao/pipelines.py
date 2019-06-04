# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import redis
import pymongo


r = redis.Redis(host='47.101.222.18',port=6379,password='wangshiji',decode_responses=True)
class BaiducitiaoPipeline(object):
    def open_spider(self,spider):
        # mongodb数据库配置
        self.mg = pymongo.MongoClient('mongodb://localhost:27017/')
        self.mydb = self.mg['baiducitiao']
        self.mycol = self.mydb['citiao']


    def process_item(self, item, spider):
        if spider.name == 'downcitiao':
            self.mycol.insert_one(item)
        else:
            r.sadd('citiaoRequests',str(item))
        return item


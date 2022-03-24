# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
from redis import Redis

class SakulaPipeline():
    def open_spider(self,spider):
        ###在爬虫开始前执行一次，用来打开文件
        print('打开文件')
        self.f = open ('data.txt','a',encoding= 'utf-8')
    def close_spider(self,spider):
        ###爬虫结束后执行一次，用来关闭文件
        print('关闭文件')
        self.f.close()
    def process_item(self, item, spider):
        print(item)
        self.f.write(item['title'] + ' ' + item['num'] + ' ' + item['link'] + '\n' )
        return item
class RedisPipeline(object):
    def open_spider(self,spider):
        ###创建服务器对象
        # self.conn = Redis(host='127.0.0.1', port='6379')
        # print(self.conn)
        pass
    def close_spider(self,spider):
        ###关闭服务器
        pass
    def process_item(self, item, spider):
        spider.conn.lpush('sakulaData',item['title'],item['num'],item['link'])
        ###优先级最高的管道类需要通过return将数据返回给优先级低的管道类!!!!!!!!!!!
        return item


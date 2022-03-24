# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy


class SakulaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    num = scrapy.Field()###集数
    title = scrapy.Field()###动漫名
    link = scrapy.Field()###下载地址

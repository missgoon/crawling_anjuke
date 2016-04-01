# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

#import scrapy
#
#
#class TuicoolMagsItem(scrapy.Item):
#    # define the fields for your item here like:
#    # name = scrapy.Field()
#    pass
from scrapy.item import Item,Field

class CityItem(Item):
  name=Field()  #城市名
  url=Field()  #关联的地址
  db_type=Field()  #数据库集合名
  house_amount=Field()  #该城市楼盘数
  date=Field()  #入数据库时间
  new_house_url=Field()  #页面新房的地址
  
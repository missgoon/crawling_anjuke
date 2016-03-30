# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

# import scrapy


# class AnjukeItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass

from scrapy.item import Item,Field

class HouseItem(Item):
  name=Field()  #楼盘名称
  status=Field()  #状态
  price=Field()  #参考单价
  property_type=Field()  #物业类型
  developer=Field()  #开发商
  area_position=Field()  #区域位置
  address=Field()  #楼盘地址
  telephone=Field()  #售楼处电话
  min_down_payment=Field()  #最低首付
  house_type=Field()  #楼盘户型
  opening_date=Field()  #开盘时间
  possession_date=Field()  #交房时间
  sales_office_add=Field()  #售楼处地址
  building_types=Field()  #建筑类型
  year_of_property=Field()  #产权年限
  fitment=Field()  #装修标准
  plot_ratio=Field()  #容积率
  greening_rate=Field()  #绿化率
  floor_condition=Field() #楼层状况
  works_programme=Field()  #工程进度
  managefee=Field()  #物业管理费
  property_management=Field()  #物业管理公司
  freeway_viaduct=Field()  #高速/高架


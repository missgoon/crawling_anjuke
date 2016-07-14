# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from pymongo import MongoClient
from datetime import datetime as DateTime
import logging
import re

class AnjukePipeline(object):
  """
    将抓取到的数据保存的all.json文件
  """
  def __init__(self):
    self.all_file=open("/root/anjuke/all.json","wb")

  def process_item(self, item, spider):
    line=json.dumps(dict(item))+"\n"
    self.all_file.write(line)
    return item

  def close_spider(self,spider):
    print("ok you're closing spider")
    self.all_file.close()

class AnjukeCityItemPipeline(object):
  """
    将抓取到的数据保存到mongodb数据库
  """
  def __init__(self):
    client = MongoClient("139.129.45.40",27017)
    db=client.anjuke
    self.cities=db.cities

  def process_item(self,item,spider):
    if item.get("db_type","false")=="cities":
      db_item=self.cities.find({"url":item["url"]})
      if db_item.count()==0:
        item["date"]=DateTime.utcnow()
        self.cities.insert_one(dict(item))
      else:
        db_item=db_item[0]
        update_item={}
        if item.get("name",None): 
          self.cities.update({"url":item["url"]},{"$set":{"name":list(set(db_item["name"]+item["name"]))}})
        if item.get("new_house_url",None):
          self.cities.update({"url":item["url"]},{"$set":{"new_house_url":item["new_house_url"]}})
    return item

class AnjukeHouseItemPipeline(object):
  def __init__(self):
    client=MongoClient("139.129.45.40",27017)
    db=client.anjuke
    self.houses=db.houses
    self.keys=["status","price","property_type","developer","address","area_position","telephone","min_down_payment","opening_date","house_type","sales_office_add","building_types","year_of_property","fitment","plot_ratio","greening_rate","floor_condition","works_programme","managefee","property_management","freeway_viaduct"]

  def process_item(self,item,spider):
    if item.get("db_type","false")=="houses" and len(item.get("db_id",""))!=0:
      db_item=self.houses.find({"db_id":item["db_id"]})
      if db_item.count()==0:
        item["date"]=DateTime.utcnow()
        self.houses.insert_one(dict(item))
      # elif len(dict(item))>len(dict(db_item)):
      #   self.houses.update({"db_id":item["db_id"]},{"$set":dict(item)})
      else:
        db_item=db_item[0]
        for key in self.keys:
          if item.get(key,None) and (item.get(key,"null")!="null" or db_item.get(key,"null")=="null"): self.houses.update_one({"db_id":db_item["db_id"]},{"$set":{key:item.get(key,"null")}})
        logging.info("######process_item:")
        logging.info(self.houses.find_one(db_item["_id"]))
    return item

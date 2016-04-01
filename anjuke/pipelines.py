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

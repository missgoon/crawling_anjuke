# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json

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

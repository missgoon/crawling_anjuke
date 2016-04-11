# -*- coding: utf-8 -*-
from pymongo import MongoClient

client=MongoClient("139.129.45.40",27017)
db=client.anjuke
houses=db.houses
count_list={}
for item in houses.find():
  name=str(len(item))
  if count_list.get(name,"null")=="null": count_list[name]=1
  else: count_list[name]+=1
print(houses.find().count())
for key,value in count_list.items():
  print(key,":",value)
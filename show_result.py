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
count_list= sorted(count_list.iteritems(), key=lambda d:d[0])
print('\033[1;32;40m')
print('*' * 50)
print("*楼盘总数:%d"%houses.find().count())
print('-' * 50)
print("*%12s  | %5s"%(str("拥有字段数"),"楼盘数"))
print('-' * 50)
for key,value in count_list:
  print("*%12s|%5s"%(str(key),str(value)))
print('*' * 50)
print('\033[0m')
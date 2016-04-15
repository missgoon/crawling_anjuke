#-*- coding: utf-8 -*-
import os
'''
   将log.txt文件合并到all_log文件，并删除log.txt文件
'''
with open("all_log","ab") as w:
  with open("log.txt","rb") as r:
    for line in r.readlines():
      w.write(line)
os.remove("log.txt")
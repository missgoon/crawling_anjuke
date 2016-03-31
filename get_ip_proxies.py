# -*- coding: utf-8 -*-
import requests
import lxml.html
import redis

url="http://www.youdaili.net/Daili/http/4304.html"
html=lxml.html.fromstring(requests.get(url).content)
r = redis.Redis(host="139.129.45.40",port=6379,db=0)
with open("ip_proxies","w") as file:
  for item in html.xpath("//span[@style='font-size:14px;']/text()"):
    try:
      item=item.strip().split("@")[0]
      file.write(item+"\n")
      r.lpush("ip_proxies",item)
      print(r.llen("ip_proxies"))
    except Exception,e:
      print(e)



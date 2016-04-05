# -*- coding: utf-8 -*-
import requests
import lxml.html
import redis

urls=[
  "http://www.youdaili.net/Daili/http/4309.html",
  "http://www.youdaili.net/Daili/http/4309_2.html",
  "http://www.youdaili.net/Daili/http/4309_3.html",
]
r = redis.Redis(host="139.129.45.40",port=6379,db=0)
r.flushall()
with open("ip_proxies","a") as file:
  def handle_item(item):
	  try:
	    item=item.strip().split("@")[0]
	    if not len(item)>0: raise
	    file.write(item+"\n")
	    r.lpush("ip_proxies",item)
	    print("%s\t%d"%(item,r.llen("ip_proxies")))
	  except Exception,e:
	    print(e)
  for url in urls:
    html=lxml.html.fromstring(requests.get(url).content)
    if len(html.xpath("//span[@style='font-size:14px;']"))>=1:
      for item in html.xpath("//span[@style='font-size:14px;']/text()"):
        handle_item(item)
    elif len(html.xpath("//div[@class='cont_font']/p/text()"))>0:
      for item in html.xpath("//div[@class='cont_font']/p/text()"):
        handle_item(item)





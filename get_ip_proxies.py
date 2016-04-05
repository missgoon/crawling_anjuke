# -*- coding: utf-8 -*-
import requests
import lxml.html
import redis
import multiprocessing  #多进程module

urls=[
  "http://www.youdaili.net/Daili/http/4309.html",
  "http://www.youdaili.net/Daili/http/4309_2.html",
  "http://www.youdaili.net/Daili/http/4309_3.html",
]
test_url="http://chaoyang.anjuke.com/"

r = redis.Redis(host="139.129.45.40",port=6379,db=0)
r.flushall()
def handle_item(item):
  try:
    item=item.strip().split("@")[0]
    if not len(item)>0: raise
    proxies = {'http':"http://"+item}
    response=requests.get(test_url,proxies=proxies,timeout=3)
    print(proxies,response)
    if response.status_code!=200: raise
    file.write(item+"\n")
    r.lpush("ip_proxies",item)
    print("%s\t%d"%(item,r.llen("ip_proxies")))
  except Exception,e:
    print(e)

def run(url):
  html=lxml.html.fromstring(requests.get(url).content)
  if len(html.xpath("//span[@style='font-size:14px;']"))>=1:
    for item in html.xpath("//span[@style='font-size:14px;']/text()"):
      handle_item(item)
  elif len(html.xpath("//div[@class='cont_font']/p/text()"))>0:
    for item in html.xpath("//div[@class='cont_font']/p/text()"):
      handle_item(item)

with open("ip_proxies","a") as file:
  for url in urls:
    p = multiprocessing.Process(target = run, args = (url,))
    p.start()
    print("ok %s"%url)

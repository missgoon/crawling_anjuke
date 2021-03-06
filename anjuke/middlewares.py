# -*- coding: utf-8 -*-
import redis
import requests
import logging
import re

class AnjukeHttpProxyMiddleware(object):
  """
    使用已经准备好的代理ip
  """
  def __init__(self):
    self.r = redis.Redis(host="139.129.45.40",port=6379,db=0)

  def process_request(self,request,spider):
    flag=True
    while flag:
      proxy_str=self.r.lpop("ip_proxies")
      # proxies = {'http':"http://"+proxy_str,}
      logging.info("######try:%s","http://"+proxy_str)
      try:
        # response=requests.get("http://chaoyang.anjuke.com/",proxies=proxies)
        self.r.incr("ip_proxies.times")
        if int(self.r.get("ip_proxies.times"))>3: raise
        # if response.status_code!=200 or int(self.r.get("ip_proxies.times"))>10: raise
        self.r.lpush("ip_proxies",proxy_str)
        flag=False
      except Exception,e:
        self.r.set("ip_proxies.times",0)
        print("failed:%s","http://"+proxy_str)
        print(e)
        self.r.rpush("ip_proxies",proxy_str)
    logging.info("######using the proxy:%s","http://"+proxy_str)
    request.meta["proxy"]="http://"+proxy_str

class AnjukeUserAgentMiddleware(object):
  '''
    change request header nealy every time
  '''
  def process_request(self,request,spider):
    agent="Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0"
    request.headers["User-Agent"]=agent

class AnjukeFilterVerificationCodeMiddleware(object):
  '''
    去掉能匹配到'captcha-verify'的需要输入验证码的页面
  '''
  def process_request(self,request,spider):
    if re.search("captcha-verify",request.url)!=None: raise
    logging.info("######the url need not verification code.")
    return None

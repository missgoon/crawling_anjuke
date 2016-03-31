# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from anjuke.items import *

class AnjukeSpider(CrawlSpider):
  name="anjuke"
  allowed_domains=["anjuke.com"]
  start_urls=[
    "http://www.anjuke.com/sy-city.html",
  ]

  rules=(
    Rule(LinkExtractor(allow=("http://www.anjuke.com/sy-city.html",)),callback="parse_all_city",follow=True),
    Rule(LinkExtractor(allow=(".fang.anjuke.com/?from=AF_Home_switchcity")),callback="parse_city"),

  )

  handle_httpstatus_list=[301]

  def parse(self,response):
    self.logger.info("######parse:%s",response.url)
    sel=Selector(response=response)
    for dd in sel.xpath("//dd"):
      for city_url in dd.xpath("./a/@href").extract():
        self.logger.info("######parse: yield:%s",response.url+city_url.strip())
        yield scrapy.Request(city_url.strip(),self.parse_one_city)

  def parse_one_city(self,response):
    try:
      sel=Selector(response=response)
      self.logger.info("######parse_one_city:%s",response.url)
      for a in sel.xpath("//a[@class='a_navnew']"):
        if a.xpath("./text()")[0].extract().strip()==unicode("新 房","utf-8"):
          self.logger.info("######parse_one_city: yield:%s",response.url+a.xpath("./@href")[0].extract())
          yield scrapy.Request(a.xpath("./@href")[0].extract(),self.parse_city)
    except Exception,e:
      self.logger.error(e)

  def parse_city(self,response):
    sel=Selector(response=response)
    self.logger.info("######parse_city:%s",response.url)
    try:
      key_list_div=sel.xpath("//div[@class='key-list']")[0]
      for div in key_list_div.xpath("./div"):
        url=div.xpath("./@data-link")[0].extract().strip()
        s=".fang.anjuke.com/loupan/"
        url_list=str(url).split(s)
        url_list[1]=url_list[1].split(".html")[0]
        real_url=url_list[0]+s+"canshu-"+url_list[1]+".html?from=loupan_tab"
        self.logger.info("######parse_city: yield:%s",response.url+real_url)
        yield scrapy.Request(real_url,self.parse_house)
    except Exception,e:
      self.logger.error(e)

  def parse_house(self,response):
    self.logger.info("######parse_house:%s successfully!!!",response.url)
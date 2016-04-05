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
  
  def parse(self,response):
    self.logger.info("######parse:%s",response.url)
    sel=Selector(response=response)
    for dd in sel.xpath("//dd"):
      for a in dd.xpath("./a"):
        item=CityItem(db_type="cities")
        item["name"]=[a.xpath("./text()")[0].extract().strip()]
        item["url"]=a.xpath("./@href")[0].extract().strip()
        self.logger.info("######parse: yield:%s",response.url+item["url"])
        yield item
        yield scrapy.Request(item["url"],self.parse_one_city,meta={"city_item":item})

  def parse_one_city(self,response):
    try:
      sel=Selector(response=response)
      self.logger.info("######parse_one_city:%s",response.url)
      city_item=response.meta["city_item"]
      for a in sel.xpath("//a[@class='a_navnew']"):
        if a.xpath("./text()")[0].extract().strip()==unicode("新 房","utf-8"):
          self.logger.info("######parse_one_city: yield:%s",response.url+a.xpath("./@href")[0].extract())
          city_item["new_house_url"]=a.xpath("./@href")[0].extract()
          yield city_item
          yield scrapy.Request(city_item["new_house_url"],self.parse_city)
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
        house_item=HouseItem(db_type="houses")
        house_item["db_id"]=url_list[1]
        yield house_item
        # yield scrapy.Request(real_url,self.parse_house)
      try:
        next_link=sel.xpath("//div[@class='pagination']")[0].xpath("./a[@class='next-page next-link']/@href")[0].extract().strip()
        if not len(next_link)>0: raise
        return scrapy.Request(next_link,self.parse_city)
      except:
        self.logger.info("######"+response.url+"city crawling finished...")
        pass
    except Exception,e:
      self.logger.error(e)

  # def parse_house(self,response):
  #   self.logger.info("######parse_house:%s successfully!!!",response.url)
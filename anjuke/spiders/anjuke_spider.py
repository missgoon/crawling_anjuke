# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor 
from scrapy.selector import Selector 
from scrapy.http import HtmlResponse

class AnjukeSpider(CrawlSpider):
  name="anjuke"
  allowed_domains=["anjuke.com"]
  start_urls=[
    "http://www.anjuke.com/sy-city.html",
  ]
  
  rules=(
  	Rule(LinkExtractor(allow=("http://www.anjuke.com/sy-city.html",)),callback="parse_all_city")
    Rule(LinkExtractor(allow=(".fang.anjuke.com/?from=AF_Home_switchcity",)),callback="parse_city"),
    Rule(LinkExtractor(allow=(".anjuke.com",)),callback="parse_one_city"),
  )

  def parse_all_city(self,response):
    sel=Selector(response=response)
    for dd in sel.xpath("//dd"):
      for city_url in dd.xpath("./a/@href").extract()
        yield scrapy.Request(city_url.strip(),self.parse_one_city)

  def parse_one_city(self,response):
    sel=Selector(response=response)
    for a in sel.xpath("//a[@class='a_navnew']"):
      if a.xpath("./text()")[0].extract()==unicode("新 房","utf-8"):
      	yield scrapy.Request(a.xpath("./@href")[0].extract(),self.parse_city)

  



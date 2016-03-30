# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor 
from scrapy.selector import Selector 
from scrapy.http import HtmlResponse
from anjuke.items import *

class AnjukeSpider(CrawlSpider):
  name="anjuke"
  allowed_domains=["anjuke.com"]
  start_urls=[
    "http://www.anjuke.com/sy-city.html",
  ]
  
  rules=(
  	Rule(LinkExtractor(allow=("http://www.anjuke.com/sy-city.html")),callback="parse_all_city"),
    Rule(LinkExtractor(allow=(".fang.anjuke.com/?from=AF_Home_switchcity")),callback="parse_city"),
    Rule(LinkExtractor(allow=("canshu-")),callback="parse_house"),
    Rule(LinkExtractor(allow=(".anjuke.com")),callback="parse_one_city"),
  )

  def parse_all_city(self,response):
    sel=Selector(response=response)
    for dd in sel.xpath("//dd"):
      for city_url in dd.xpath("./a/@href").extract():
        yield scrapy.Request(city_url.strip(),self.parse_one_city)

  def parse_one_city(self,response):
    try:
      sel=Selector(response=response)
      for a in sel.xpath("//a[@class='a_navnew']"):
        if unicode(a.xpath("./text()")[0].extract(),"utf-8")==unicode("新 房","utf-8"):
         	yield scrapy.Request(a.xpath("./@href")[0].extract(),self.parse_city)
    except Exception,e:
      print(e)

  def parse_city(self,response):
    sel=Selector(response=response)
    key_list_div=sel.xpath("//div[@class='key-list']")[0]
    for div in key_list_div.xpath("./div"):
      url=div.xpath("./@data-link")[0].extract().strip()
      s=".fang.anjuke.com/loupan/"
      url_list=str(url).split(s)
      url_list[1]=url_list[1].split(".html")[0]
      real_url=url_list[0]+s+"canshu-"+url_list[1]+".html?from=loupan_tab"
      yield scrapy.Request(real_url,self.parse_house)

  def parse_house(self,response):
    sel=Selector(response=response)
    divs=sel.xpath("//div[@class='can-container clearfix']")[0].xpath("./div[@class='can-left']")[0].xpath("./div[@class='can-item']")
    #楼盘名称  状态
    li_for_name_status=divs[0].xpath("./div/ul[@class='list']/li")[0]
    name=li_for_name_status.xpath("./div[@class='des']/text()")[0].extract().strip()
    status=li_for_name_status.xpath("./div[@class='des']/i[@class='can-tag-status lp-tag-status lp-tag-status-xian']/text()")[0].extract().strip()
    #price：住宅 3400 元/m²，由三部分组成
    li_for_price=divs[0].xpath("./div/ul[@class='list']/li")[1]
    price_part1=li_for_price.xpath("./div[@class='des']/text()")[0].extract().strip()  #
    price_part2=li_for_price.xpath("./div[@class='des']/span[@class='can-spe can-big space2']/text()")[0].extract().strip()
    price_part3="".join(li_for_price.xpath("./div[@class='des']").extract()).split("</span>")[-1].split("<a")[0].strip()
    price=price_part1+" "+price_part2+" "+price_part3
    #property_type
    property_type=divs[0].xpath("./div/ul[@class='list']/li")[2].xpath("./div[@class='des']/text()")[0].extract().strip()
    #developer
    developer=divs[0].xpath("./div/ul[@class='list']/li")[3].xpath("./div[@class='des']/a/text()")[0].extract().strip()
    #area_position
    area_position="-".join(divs[0].xpath("./div/ul[@class='list']/li")[4].xpath("./div[@class='des']/a/text()").extract())
    #address
    address=divs[0].xpath("./div/ul[@class='list']/li")[5].xpath("./div[@class='des']/text()")[0].extract().strip()
    #telephone
    telephone=" ".join(divs[0].xpath("./div/ul[@class='list']/li")[6].xpath("./div[@class='des']")[0].xpath("./span").extract())
    #min_down_payment  house_type  opening_date  possession_date
    lis=divs[1].xpath("./div/ul[@class='list']/li")
    fields=[]
    for i in range(0,len(lis)):
      fields.append(lis[i].xpath("./div[@class='des']/text()")[0].extract().strip())
    min_down_payment,house_type,opening_date,possession_date,sales_office_add=fields
    #building_types,year_of_property,fitment,plot_ratio,greening_rate,floor_condition,works_programme,managefee
    lis=divs[2].xpath("./div/ul[@class='list']/li")
    fields=[]
    for i in range(0,len(lis)-1):
      fields.append(lis[i].xpath("./div[@class='des']/text()")[0].extract().strip())
    building_types,year_of_property,fitment,plot_ratio,greening_rate,floor_condition,works_programme,managefee=fields
    
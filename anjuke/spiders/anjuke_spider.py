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
        yield scrapy.Request(real_url,self.parse_house)
      try:
        next_link=sel.xpath("//div[@class='pagination']")[0].xpath("./a[@class='next-page next-link']/@href")[0].extract().strip()
        if not len(next_link)>0: raise
        self.logger.info("######from %s get next link %s"%(response.url,next_link))
        yield scrapy.Request(next_link,self.parse_city)
      except:
        self.logger.info("######"+response.url+"city crawling finished...")
        pass
    except Exception,e:
      self.logger.error(e)

  def parse_house(self,response):
    sel=Selector(response=response)
    self.logger.info("parse_house:%s",response.url)
    item=HouseItem()
    try:
      divs=sel.xpath("//div[@class='can-container clearfix']")[0].xpath("./div[@class='can-left']")[0].xpath("./div[@class='can-item']")
      #楼盘名称  状态
      li_for_name_status=divs[0].xpath("./div/ul[@class='list']/li")[0]
      item["name"]=li_for_name_status.xpath("./div[@class='des']/text()")[0].extract().strip()
      item["status"]=li_for_name_status.xpath("./div[@class='des']/i/text()")[0].extract().strip()
      #price：住宅 3400 元/m²，由三部分组成
      li_for_price=divs[0].xpath("./div/ul[@class='list']/li")[1]
      price_part1=li_for_price.xpath("./div[@class='des']/text()")[0].extract().strip()
      price_part2=li_for_price.xpath("./div[@class='des']/span[@class='can-spe can-big space2']/text()")[0].extract().strip()
      price_part3="".join(li_for_price.xpath("./div[@class='des']").extract()).split("</span>")[-1].split("<a")[0].strip()
      item["price"]=price_part1+" "+price_part2+" "+price_part3
      #property_type
      item["property_type"]=divs[0].xpath("./div/ul[@class='list']/li")[2].xpath("./div[@class='des']/text()")[0].extract().strip()
      #developer
      item["developer"]=divs[0].xpath("./div/ul[@class='list']/li")[3].xpath("./div[@class='des']/a/text()")[0].extract().strip()
      #area_position
      item["area_position"]="-".join(divs[0].xpath("./div/ul[@class='list']/li")[4].xpath("./div[@class='des']/a/text()").extract())
      #address
      item["address"]=divs[0].xpath("./div/ul[@class='list']/li")[5].xpath("./div[@class='des']/text()")[0].extract().strip()
      #telephone
      item["telephone"]=" ".join(divs[0].xpath("./div/ul[@class='list']/li")[6].xpath("./div[@class='des']")[0].xpath("./span").extract())
      #min_down_payment  house_type  opening_date  possession_date
      lis=divs[1].xpath("./div/ul[@class='list']/li")
      fields=[]
      for i in range(0,len(lis)):
        fields.append(lis[i].xpath("./div[@class='des']/text()")[0].extract().strip())
      item["min_down_payment"],item["house_type"],item["opening_date"],item["possession_date"],item["sales_office_add"]=fields
      #building_types,year_of_property,fitment,plot_ratio,greening_rate,floor_condition,works_programme,managefee,property_management
      lis=divs[2].xpath("./div/ul[@class='list']/li")
      fields=[]
      for i in range(0,len(lis)-1):
        fields.append(lis[i].xpath("./div[@class='des']/text()")[0].extract().strip())
      item["building_types"],item["year_of_property"],item["fitment"],item["plot_ratio"],item["greening_rate"],item["floor_condition"],item["works_programme"],item["managefee"]=fields
      item["property_management"]=lis[8].xpath("./div[@class='des']/a/text()")[0].extract().strip()
      #freeway_viaduct
      item["freeway_viaduct"]=divs[3].xpath("./div/ul[@class='list']/li")[0].xpath("./div[@class='des']/text()")[0].extract().strip()
      return item
    except Exception,e:
      self.logger.error(e)
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

  def fun1(self,div):
    """抓取house信息"""
    result=HouseItem()
    li_list={u"楼盘名称":self.fun5,u"参考单价":self.fun6,u"物业类型":self.fun7,u"开发商":self.fun8,u"区域位置":self.fun9,u"楼盘地址":self.fun10,u"售楼处电话":self.fun11}
    for li in div.xpath("./div[@class='can-border']/ul[@class='list']/li"):
      try:
        item_hash=li_list.get(li.xpath("./div[@class='name']/text()")[0].extract().strip(),self.return_none)(li)
        if item_hash!="null": result.update(item_hash)
      except:
        pass
    return result 

  def fun5(self,li):
    """抓取名称，状态"""
    try:
      name=li.xpath("./div[@class='des']/text()")[0].extract().strip()
    except:
      name="null"
    try:
      status=li.xpath("./div[@class='des']/i/text()")[0].extract().strip()
    except:
      status="null"
    return {"name":name,"status":status}

  def fun6(self,li):
    """抓取参考单价"""
    try:
      price=li.xpath("./div[@class='des']/text()")[0].extract().strip()+"-"+li.xpath("./div[@class='des']/span/text()")[0].extract().strip()+"-"+li.xpath("./div[@class='des']/text()")[1].extract().strip()
    except:
      price="null"
    return {"price":price}

  def fun7(self,li):
    """抓取物业类型"""
    try:
      for text in li.xpath("./div[@class='des']/text()"):
        property_type+=" "+text.extract().strip()
    except:
      property_type="null"
    return {"property_type":property_type.strip()}

  def fun8(self,li):
    """抓取开发商"""
    try:
      developer=li.xpath("./div[@class='des']/a/text()")[0].extract().strip()
    except:
      developer="null"
    return {"developer":developer}

  def fun9(self,li):
    """抓取区域位置"""
    try:
      area_position=""
      for a in li.xpath("./div[@class='des']/a"):
        area_position+=" "+a.xpath("./text()")[0].extract().strip()
    except:
      area_position="null"
    return {"area_position":area_position.strip()}

  def fun10(self,li):
    """抓取楼盘地址"""
    try:
      address=li.xpath("./div[@class='des']/text()")[0].extract().strip()
    except:
      address="null"
    return {"address":address}

  def fun11(self,li):
    """抓取售楼处电话"""
    try:
      telephone=""
      for span in li.xpath("./div[@class='des']/span"):
        telephone+=" "+span.xpath("./text()")[0].extract().strip()
    except:
      telephone="null"
    return {"telephone":telephone.strip()}

  def fun2(self,div):
    lis=div.xpath("./div/ul[@class='list']/li")
    result,names=HouseItem(),["min_down_payment","house_type","opening_date","possession_date","sales_office_add","building_types","year_of_property","fitment","plot_ratio","greening_rate","floor_condition","works_programme","managefee"]
    for i in range(0,len(lis)):
      try:
        name=lis[i].xpath("./div[@class='name']/text()")[0].extract().strip()
        if names.count(name)!=0: 
          try:
            rst=lis[i].xpath("./div[@class='des']/text()")[0].extract().strip()
          except:
            rst="null"
          result[name.encode("utf-8")]=rst
        elif name==u"物业管理费":
          result["property_management"]=lis[8].xpath("./div[@class='des']/a/text()")[0].extract().strip()
      except:
        pass
    return result

  def fun3(self,div):
    result=HouseItem()
    result["freeway_viaduct"]=div.xpath("./div/ul[@class='list']/li")[0].xpath("./div[@class='des']/text()")[0].extract().strip()
    return result

  def return_none(self,args):
    return "none"

  def parse_house(self,response):
    sel=Selector(response=response)
    self.logger.info("parse_house:%s",response.url)
    item=HouseItem(db_type="houses",db_id=response.url.split("canshu-")[1].split(".html")[0])
    can_head={u"基本信息":self.fun1,u"销售信息":self.fun2,u"小区情况":self.fun2,u"交通配套":self.fun3}
    try:
      for div in sel.xpath("//div[@class='can-left']/div[@class='can-item']"):
        rst=can_head.get(div.xpath("./div[@class='can-head']/h4/text()")[0].extract().strip(),self.return_none)(div)
        if len(rst)>0 and rst!="none": item.update(rst)
    except Exception,e:
      self.logger.error(e)
    finally:
      self.logger.info("######get item successfully!!!!",item)
      return item











      # divs=sel.xpath("//div[@class='can-container clearfix']")[0].xpath("./div[@class='can-left']")[0].xpath("./div[@class='can-item']")
      # #楼盘名称  状态
      # li_for_name_status=divs[0].xpath("./div/ul[@class='list']/li")[0]
      # item["name"]=li_for_name_status.xpath("./div[@class='des']/text()")[0].extract().strip()
      # item["status"]=li_for_name_status.xpath("./div[@class='des']/i/text()")[0].extract().strip()

      # #price：住宅 3400 元/m²，由三部分组成
      # li_for_price=divs[0].xpath("./div/ul[@class='list']/li")[1]
      # price_part1=li_for_price.xpath("./div[@class='des']/text()")[0].extract().strip()
      # price_part2=li_for_price.xpath("./div[@class='des']/span[@class='can-spe can-big space2']/text()")[0].extract().strip()
      # price_part3="".join(li_for_price.xpath("./div[@class='des']").extract()).split("</span>")[-1].split("<a")[0].strip()
      # item["price"]=price_part1+" "+price_part2+" "+price_part3
      # #property_type
      # item["property_type"]=divs[0].xpath("./div/ul[@class='list']/li")[2].xpath("./div[@class='des']/text()")[0].extract().strip()
      # #developer
      # item["developer"]=divs[0].xpath("./div/ul[@class='list']/li")[3].xpath("./div[@class='des']/a/text()")[0].extract().strip()
      # #area_position
      # item["area_position"]="-".join(divs[0].xpath("./div/ul[@class='list']/li")[4].xpath("./div[@class='des']/a/text()").extract())
      # #address
      # item["address"]=divs[0].xpath("./div/ul[@class='list']/li")[5].xpath("./div[@class='des']/text()")[0].extract().strip()
      # #telephone
      # item["telephone"]=" ".join(divs[0].xpath("./div/ul[@class='list']/li")[6].xpath("./div[@class='des']")[0].xpath("./span").extract())
      #min_down_payment  house_type  opening_date  possession_date
      # lis=divs[1].xpath("./div/ul[@class='list']/li")
      # fields=[]
      # for i in range(0,len(lis)):
      #   fields.append(lis[i].xpath("./div[@class='des']/text()")[0].extract().strip())
      # item["min_down_payment"],item["house_type"],item["opening_date"],item["possession_date"],item["sales_office_add"]=fields
      # #building_types,year_of_property,fitment,plot_ratio,greening_rate,floor_condition,works_programme,managefee,property_management
      # lis=divs[2].xpath("./div/ul[@class='list']/li")
      # fields=[]
      # for i in range(0,len(lis)-1):
      #   fields.append(lis[i].xpath("./div[@class='des']/text()")[0].extract().strip())
      # item["building_types"],item["year_of_property"],item["fitment"],item["plot_ratio"],item["greening_rate"],item["floor_condition"],item["works_programme"],item["managefee"]=fields
      # item["property_management"]=lis[8].xpath("./div[@class='des']/a/text()")[0].extract().strip()
      # #freeway_viaduct
      # item["freeway_viaduct"]=divs[3].xpath("./div/ul[@class='list']/li")[0].xpath("./div[@class='des']/text()")[0].extract().strip()
      # return item







    #   fields.append(rst)
    # result["min_down_payment"],result["house_type"],result["opening_date"],result["possession_date"],result["sales_office_add"]=fields

  # def fun3(div):
  #   """
  #     building_types,year_of_property,fitment,plot_ratio,greening_rate,floor_condition,works_programme,managefee,property_management
  #   """
  #   lis=divs.xpath("./div/ul[@class='list']/li")
  #   fields=[]
  #   result=HouseItem()
  #   for i in range(0,len(lis)-1):
  #     try:
  #       rst=lis[i].xpath("./div[@class='des']/text()")[0].extract().strip()
  #     except:
  #       rst="null"
  #     fields.append(rst)
  #   result["building_types"],result["year_of_property"],result["fitment"],result["plot_ratio"],result["greening_rate"],result["floor_condition"],result["works_programme"],result["managefee"]=fields
  #   result["property_management"]=lis[8].xpath("./div[@class='des']/a/text()")[0].extract().strip()
  #   return result





          # rst=fun1(div.xpath("./div[@class='can-head']/h4/text()")[0].extract().strip())

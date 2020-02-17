# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import CsvItemExporter
from cassandra.cluster import Cluster
from openpyxl import Workbook

class Edgarxlsxspider(object):
    wb = Workbook()
    ws = wb.active
    ws.append(['company','date','type','clk','clk_url','ten_year_url','body_url','seven_body','sevenA_body'])

    def process_item(self, item, spider):
        line = [item['company'], item['date'], item['type'], item['clk'], \
                item['clk_url'], item['ten_year_url'], item['body_url'], \
                item['seven_body'], item['sevenA_body']]
        self.ws.append(line)
        self.wb.save('edgar.xlsx')
        return item

class EdgarPipeline(object):
    def __init__(self):
        self.server = ['13.229.248.211']
        self.cluster = Cluster(self.server)
        self.session = self.cluster.connect('scrapy')

    def process_item(self, item, spider):
        self.session.execute("""insert into edgar_seven (company,date,type,clk,clk_url,ten_year_url,body_url,seven_body,sevenA_body)values(%s ,%s ,%s, %s, %s ,%s ,%s, %s, %s)""",
                        (str(item['company']),str(item['date']),str(item['type']),str(item['clk']), str(item['clk_url']),str(item['ten_year_url']),
                         str(item['body_url']),str(item['seven_body']),str(item['sevenA_body'])))
        return item

class EdgarfetchPipeline(object):

    def __init__(self):
        self.server = ['52.76.70.227']
        self.cluster = Cluster(self.server)
        self.session = self.cluster.connect('scrapy')

    def process_item(self, item, spider):
        self.session.execute("""insert into edgar (company,date,type,clk,clk_url,ten_year_url,body_url,body)values(%s ,%s ,%s, %s, %s ,%s ,%s, %s)""",
                        (str(item['company']),str(item['date']),str(item['type']),str(item['clk']), str(item['clk_url']),str(item['ten_year_url']),
                         str(item['body_url']),str(item['body'])))
        return item

class HangsengPipeline(object):

    def __init__(self):
        self.server = ['52.76.70.227']
        self.cluster = Cluster(self.server)
        self.session = self.cluster.connect('scrapy')

    def process_item(self, item, spider):
        self.session.execute("""insert into hangseng (constituent_type,constituent_name,code)values(%s ,%s ,%s)""",
                        (str(item['constituent_type']),str(item['constituent_name']),str(item['code'])))
        return item

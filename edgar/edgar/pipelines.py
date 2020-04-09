# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import CsvItemExporter
from cassandra.cluster import Cluster
from openpyxl import Workbook
import re

class Edgarxlsxspider(object):
    wb = Workbook()
    ws = wb.active
    ws.append(['company','date','type','clk','clk_url','ten_year_url','body_url','seven_body_number',\
               'seven_body_1','seven_body_2','seven_body_3','seven_body_4','seven_body_5',\
               'seven_body_6','seven_body_7','seven_body_8','is_item_seven'])

    def process_item(self, item, spider):
        line = [item['company'], item['date'], item['type'], item['clk'], \
                item['clk_url'], item['ten_year_url'], item['body_url'], \
                item['seven_body_number'],item['seven_body_1'],item['seven_body_2'],\
                item['seven_body_3'],item['seven_body_4'],item['seven_body_5'],\
                item['seven_body_6'],item['seven_body_7'],item['seven_body_8'],item['is_item_seven']]
        # for info in line:
        #     self.ws.append(info)
        self.ws.append(line)
        pattern = re.compile(r'\d+\.?\d*')
        clk = pattern.findall(item['clk'])[0] if len(pattern.findall(item['clk']))>0 else item['clk']
        self.wb.save(f"{clk}.xlsx".replace("'",''))
        return item

class EdgarcsvPipeline(object):
    def open_spider(self, spider):
        self.file = open('edgar.csv', 'wb')
        self.exporter = CsvItemExporter(self.file, delimiter='~')
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class EdgarPipeline(object):
    def __init__(self):
        self.server = ['13.229.248.211']
        self.cluster = Cluster(self.server)
        self.session = self.cluster.connect('scrapy')

    def process_item(self, item, spider):
        self.session.execute("""insert into edgar_seven (company,date,type,clk,clk_url,ten_year_url,body_url,seven_body,sevena_body)values(%s ,%s ,%s, %s, %s ,%s ,%s, %s, %s)""",
                        (str(item['company']),str(item['date']),str(item['type']),str(item['clk']), str(item['clk_url']),str(item['ten_year_url']),
                         str(item['body_url']),str(item['seven_body']),str(item['is_item_seven'])))
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

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exporters import CsvItemExporter
from cassandra.cluster import Cluster

class EdgarPipeline(object):
    def open_spider(self, spider):
        self.file = open('output.csv', 'wb')
        self.exporter = CsvItemExporter(self.file, delimiter='~')
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class EdgarfetchPipeline(object):

    def __init__(self):
        self.server = ['52.76.70.227']
        self.cluster = Cluster(self.server)
        self.session = self.cluster.connect('scrapy')

    def process_item(self, item, spider):
        self.session.execute("""insert into edgars (company,date,type,clk,clk_url,ten_year_url,body_url,body)values(%s ,%s ,%s, %s, %s ,%s ,%s, %s)""",
                        (str(item['company']),str(item['date']),str(item['type']),str(item['clk']), str(item['clk_url']),str(item['ten_year_url']),
                         str(item['body_url']),str(item['body'])))
        return item

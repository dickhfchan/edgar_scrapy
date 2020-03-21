# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.shell import inspect_response
import pandas as pd

from item7.items import Item7Item


class ExampleSpider(scrapy.Spider):
    name = 'example'

    def start_requests(self):
        urls = pd.read_excel('E:\Programacao\Scrapy\Dick Chan\item7\edgar.xlsx').body_url.tolist()
        for url in urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        item = Item7Item()
        item_7_possible_titles = ['DISCUSSION AND ANALYSIS OF']
        item_8_possible_titles = ['FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA', 'CONSOLIDATED FINANCIAL STATEMENTS']
        for item_seven_title in item_7_possible_titles:
            for item_8_title in item_8_possible_titles:
                item_seven_xpath = f'text()[contains(., "{item_seven_title}")]'
                item_8_xpath = f'text()[contains(., "{item_8_title}")]'
                # I am selecting all the nodes before node 2 and all the nodes from node 1
                # and removing the nodes of node 1
                # from node 2. This way I am selecting all the information between items 7 and 8
                item_seven = response.xpath(f'set:difference(/*/*//{item_8_xpath}/preceding::'
                                            f'*, /*/*//{item_seven_xpath}/preceding::*)'
                                            f'/*[not(ancestor::td)]//text()').getall()
                if item_seven:
                    break
            if item_seven:
                break
        # Remove page numbers
        item_seven_no_ints = [element.strip() for element in item_seven
                              if re.match(r'^-?\d+(?:\.\d+)?$', element.strip()) is None]
        # Remove blank list values
        item_seven_final = list(filter(None, item_seven_no_ints))
        file_name = response.url.split('/')[-1].split('.')[0]
        # with open(f'text_files/{file_name}.txt', 'w') as f:
        #     f.write(r'\n'.join(item_seven_final))
        item['item_seven'] = item_seven_final
        yield item

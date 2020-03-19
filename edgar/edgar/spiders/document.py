# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.shell import inspect_response
from item7.items import Item7Item


class ExampleSpider(scrapy.Spider):
    name = 'example'

    def start_requests(self):
        urls = ['https://www.sec.gov/Archives/edgar/data/1058090/000119312514035451/d629534d10k.htm',
                  'https://www.sec.gov/Archives/edgar/data/1058090/000119312513046377/d445653d10k.htm',
                  'https://www.sec.gov/Archives/edgar/data/1058090/000119312515033771/d861905d10k.htm',
                  'https://www.sec.gov/Archives/edgar/data/1058090/000105809016000058/cmg-20151231x10k.htm',
                  'https://www.sec.gov/Archives/edgar/data/1058090/000119312510035029/d10k.htm',
                  'https://www.sec.gov/Archives/edgar/data/1058090/000105809017000009/cmg-20161231x10k.htm',
                  'https://www.sec.gov/Archives/edgar/data/1058090/000119312512052969/d280751d10k.htm',
                  'https://www.sec.gov/Archives/edgar/data/1058090/000105809020000010/cmg-20191231x10k.htm',
                  'https://www.sec.gov/Archives/edgar/data/1058090/000105809019000007/cmg-20181231x10k.htm',
                  'https://www.sec.gov/Archives/edgar/data/1058090/000105809018000018/cmg-20171231x10k.htm',
                  'https://www.sec.gov/Archives/edgar/data/1058090/000119312511039010/d10k.htm'
]
        for url in urls:
            yield scrapy.Request(url, callback=self.parse, encoding='utf-8-sig')

    def parse(self, response):
        item = Item7Item()
        n1 = 'text()[contains(., "DISCUSSION AND ANALYSIS OF")]'
        n2 = 'text()[contains(., "FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA ")]'
        # I am selecting all the nodes before node 2 and all the nodes from node 1 and removing the nodes of node 1
        # from node 2. This way I am selecting all the information between items 7 and 8
        item_seven = response.xpath(f'set:difference(/*/*//{n2}/preceding::p, /*/*//{n1}/preceding::p)'
                                    f'/*[not(ancestor::td)]//text()').getall()
        # Remove page numbers
        item_seven_no_ints = [element.strip() for element in item_seven
                              if re.match(r'^-?\d+(?:\.\d+)?$', element.strip()) is None]
        # Remove blank list values
        item_seven_final = list(filter(None, item_seven_no_ints))
        with open('test_file.txt', 'w') as f:
            f.write(r'\n'.join(item_seven_final))
        item['item_seven'] = item_seven_final
        yield item

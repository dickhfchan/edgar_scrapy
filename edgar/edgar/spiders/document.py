# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.shell import inspect_response
from item7.items import Item7Item


class ExampleSpider(scrapy.Spider):
    name = 'example'
    start_urls = [r"file:///C:\Users\Pichau\Downloads\form10k.html"]

    def parse(self, response):
        item = Item7Item()
        # Select all the tags that are in the body, only the first child of the <text>
        all_selectors = response.xpath('//text/*')
        # Select the item tags by their title
        item_seven_head = [x.xpath('.//text()[contains(., "DISCUSSION")]') for x in all_selectors]
        item_seven_a_head = [x.xpath('.//text()[contains(., "QUANTITATIVE AND QUALITATIVE")]') for x in all_selectors]
        # This one represents the edge of the item_seven_a_tag
        item_8_head = [x.xpath('.//text()[contains(., "FINANCIAL STATEMENTS")]') for x in all_selectors]
        for i in range(len(item_seven_a_head)):
            if len(item_seven_head[i]) != 0:
                item_seven_head_index = i
            if len(item_seven_a_head[i]) != 0:
                item_seven_a_head_index = i
            if len(item_8_head[i]) != 0:
                item_8_head_index = i
        # Select the information we need
        if 'item_seven_a_head_index' in locals():
            item_seven = all_selectors[item_seven_head_index:item_seven_a_head_index]
        else:
            item_seven = all_selectors[item_seven_head_index:item_8_head_index]
        # Remove tables from the results
        item_seven = item_seven.xpath('./font//text()').getall()
        # Remove page numbers
        item_seven_no_ints = [element.strip() for element in item_seven
                              if re.match(r'^-?\d+(?:\.\d+)?$', element.strip()) is None]
        # Remove blank list values
        item_seven_final = list(filter(None, item_seven_no_ints))
        with open('test_file.txt', 'w') as f:
            f.write(r'\n'.join(item_seven_final))
        item['item_seven'] = item_seven_final
        yield item

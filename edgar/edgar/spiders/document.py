# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.shell import inspect_response
from edgar.items import DocumentItem


# The 'example' spider has all the code that is needed and the "parse" method can be
# pasted to any callback of an spider which will give the document's html response.
# Please change the method name so it doesn't change the behaviour of the default
# parse method of the spider.
# The "item_seven_final" and "item_seven_a_final" are lists that can be joined
# if needed. They are clean and have all the information in the items excluding
# the tables.
class DocumentSpider(scrapy.Spider):
    name = 'document'
    start_urls = ['document_url']

    def parse(self, response):
        item = DocumentItem()
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
        item_seven = all_selectors[item_seven_head_index:item_seven_a_head_index]
        item_seven_a = all_selectors[item_seven_a_head_index:item_8_head_index]
        # Remove tables from the results
        item_seven = item_seven.xpath('./font//text()').getall()
        item_seven_a = item_seven_a.xpath('./font//text()').getall()
        # Remove page numbers
        item_seven_no_ints = [element.strip() for element in item_seven
                              if re.match(r'^-?\d+(?:\.\d+)?$', element.strip()) is None]
        item_seven_a_no_ints = [element.strip() for element in item_seven_a
                              if re.match(r'^-?\d+(?:\.\d+)?$', element.strip()) is None]
        # Remove blank list values
        item_seven_final = list(filter(None, item_seven_no_ints))
        item_seven_a_final = list(filter(None, item_seven_a_no_ints))
        # Please add items
        item['item_seven'] = item_seven_final
        item['item_sevena'] = item_seven_a_final
        yield item

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
        # Here I am selecting all the tags that have the text body, this means that I am selecting the parent tag
        # that have all the <p> tags with texts in it. Sometimes the parent tag is not the <text>, because inside the
        # text are two div tags, where the second is the parent tag we are looking for. If the script is not returning
        # any values, this means that the text is not following the template that was analyzed. If this happens, please
        # look at the document format and add an if statement to work with the specific document.
        all_selectors = response.xpath('//text/*')
        if len(all_selectors) == 3:
            all_selectors = response.xpath('//text/div[2]/*')
        # Select the item tags by their title
        item_seven_head = [x.xpath('.//text()[contains(., "DISCUSSION AND ANALYSIS OF")]') for x in all_selectors]
        # This one represents the edge of the item_seven_a_tag
        item_8_head = [x.xpath('.//text()[contains(., "FINANCIAL STATEMENTS")]') for x in all_selectors]
        for i in range(len(item_seven_head)):
            if len(item_seven_head[i]) != 0:
                item_seven_head_index = i
            if len(item_8_head[i]) != 0:
                item_8_head_index = i
        # Select the information we need
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

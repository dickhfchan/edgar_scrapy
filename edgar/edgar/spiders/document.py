# -*- coding: utf-8 -*-
import scrapy
import w3lib.html
import re
from scrapy.shell import inspect_response
import pandas as pd

from item7.items import Item7Item


class ExampleSpider(scrapy.Spider):
    name = 'example'

    # The commented lines are lines that were cleaning the data a little too much, causing some words to not have
    # spaces between them.
    def clean_html(self, text) -> str:
        # body_without_tables = w3lib.html.remove_tags_with_content(text, which_ones=('table',))
        # body_without_escape_chars = w3lib.html.replace_escape_chars(text)
        # cleaned_body = w3lib.html.strip_html5_whitespace(body_without_escape_chars)
        replaced_entities = w3lib.html.replace_entities(text)
        return replaced_entities

    def start_requests(self):
        urls = pd.read_excel('E:\Programacao\Scrapy\Dick Chan\item7\edgar2.xlsx').body_url.tolist()
        for url in urls:
            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        item = Item7Item()
        item_seven = []
        cleaned_body = self.clean_html(response.body)
        # Removing the start of the document so we won't find the item 7 in the index
        start_of_document_index = int(len(cleaned_body)/20)
        cleaned_body = cleaned_body[start_of_document_index:]
        # Replacing cleaned response's body to use the xpath in it
        response = response.replace(body=cleaned_body)
        # Looking for possible titles of the item 7 and item 8
        item_7_possible_titles = ['Item 7.', 'ITEM 7.', 'DISCUSSION AND ANALYSIS OF',
                                  'Discussion and Analysis of Financial']
        item_8_possible_titles = ['Item 8.', 'ITEM 8.', 'FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA',
                                  'Financial Statements and Supplementary Data', 'Statements and Supplementary',
                                  'Consolidated Financial Statements',
                                  'CONSOLIDATED FINANCIAL STATEMENTS']
        # Looping all possibble title combinations to find the correct one. All wrong combinations are discarted
        for item_seven_title in item_7_possible_titles:
            for item_8_title in item_8_possible_titles:
                item_seven_xpath = f'text()[contains(., "{item_seven_title}")]'
                item_8_xpath = f'text()[contains(., "{item_8_title}")]'
                item_seven_xpath_to_diff = f'/*/*//{item_seven_xpath}/preceding::*'
                item_8_xpath_to_diff = f'/*/*//{item_8_xpath}/preceding::*'
                # I am selecting all the nodes before node 2 and all the nodes from node 1
                # and removing the nodes of node 1
                # from node 2. This way I am selecting all the information between items 7 and 8
                if response.xpath(item_seven_xpath_to_diff) and response.xpath(item_8_xpath_to_diff):
                    item_xpath = f'set:difference({item_8_xpath_to_diff}, {item_seven_xpath_to_diff})' \
                                 f'/*//text()[not(ancestor-or-self::table)]'
                    item_seven = response.xpath(item_xpath).getall()
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
        is_item_seven = 1 if len(item_seven_final) < 1500 else 0
        item['item_seven'] = item_seven_final
        item['is_item_seven'] = is_item_seven
        item['url'] = response.url
        yield item

# -*- coding: utf-8 -*-
import scrapy
import w3lib.html
import re, math
from edgar.items import EdgarItem
from scrapy.shell import inspect_response


class EdgarTestSpider(scrapy.Spider):
    name = 'edgar_test'
    start_urls = ['https://www.sec.gov/Archives/edgar/data/1101215/000110121520000049/ads-20191231x10k.htm?%EF%BB%BF',
                  'https://www.sec.gov/Archives/edgar/data/766704/000095012310018352/l38660e10vk.htm?%EF%BB%BF',
                  'https://www.sec.gov/Archives/edgar/data/103379/000095012311021306/w81729e10vk.htm?%EF%BB%BF',
                  'https://www.sec.gov/Archives/edgar/data/352915/000119312514073337/d649956d10k.htm?%EF%BB%BF',
                  'https://www.sec.gov/Archives/edgar/data/740260/000119312510035246/d10k.htm?%EF%BB%BF']
    custom_settings = {
        'ITEM_PIPELINES': {
                'edgar.pipelines.Edgartestspider': 400
                }
        }

    def clean_html(self, text) -> str:
        # body_without_tables = w3lib.html.remove_tags_with_content(text, which_ones=('table',))
        # body_without_escape_chars = w3lib.html.replace_escape_chars(text)
        # cleaned_body = w3lib.html.strip_html5_whitespace(body_without_escape_chars)
        replaced_entities = w3lib.html.replace_entities(text)
        return replaced_entities

    def look_for_bold_tags(self, response, item_7_possible_titles, item_8_possible_titles, bold=True):
        item_seven = []
        for item_seven_title in item_7_possible_titles:
            for item_8_title in item_8_possible_titles:
                if bold == True:
                    item_seven_xpath = f'font[contains(@style, "bold")]//text()[contains(., "{item_seven_title}")]'
                    item_8_xpath = f'font[contains(@style, "bold")]//text()[contains(., "{item_8_title}")]'
                else:
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
        return item_seven

    def parse(self, response):
        item = EdgarItem()
        cleaned_body = self.clean_html(response.body)
        # Removing the start of the document so we won't find the item 7 in the index
        start_of_document_index = int(len(cleaned_body)/25)
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
        item_seven = self.look_for_bold_tags(response, item_7_possible_titles, item_8_possible_titles)
        if not item_seven:
            item_seven = self.look_for_bold_tags(response, item_7_possible_titles, item_8_possible_titles, bold=False)
        # Remove page numbers
        c = str.maketrans("\x92-\x94-\x93-\x96-\x97", '" " " " "')
        item_seven_no_ints = [' '.join(element.split()).translate(c).replace('Table of Contents','') for element in item_seven
                              if re.match(r'^-?\d+(?:\.\d+)?$', element.strip()) is None]
        # Remove blank list values
        item_seven_final = list(filter(None, item_seven_no_ints))
        is_item_seven = 1 if len(item_seven_final) < 1500 else 0
        item['seven_body'] = ''.join(item_seven_final)
        item['is_item_seven'] = is_item_seven
        item['url'] = response.url
        yield item

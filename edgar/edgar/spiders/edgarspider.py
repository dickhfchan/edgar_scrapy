# -*- coding: utf-8 -*-
import scrapy
import w3lib.html
import re, math
from edgar.items import EdgarItem
from scrapy.shell import inspect_response


class EdgarspiderSpider(scrapy.Spider):
    name = 'edgarspider'
    # allowed_domains = [''https://en.wikipedia.org/']
    start_urls = ['https://en.wikipedia.org/wiki/List_of_S%26P_500_companies']
    # custom_settings = {
    #     'ITEM_PIPELINES': {
    #             'edgar.pipelines.Edgarxlsxspider': 400
    #             }
    #     }

    def clean_html(self, text) -> str:
        # body_without_tables = w3lib.html.remove_tags_with_content(text, which_ones=('table',))
        # body_without_escape_chars = w3lib.html.replace_escape_chars(text)
        # cleaned_body = w3lib.html.strip_html5_whitespace(body_without_escape_chars)
        replaced_entities = w3lib.html.replace_entities(text)
        return replaced_entities

    def parse(self, response):
        # get clks datas
        clks = response.xpath('//*[@id="constituents"]/tbody/tr/td[8]/text()').extract()
        companys = response.xpath('//*[@id="constituents"]/tbody/tr/td[2]/a/text()').extract()
        Types = ['10-K','10-Q','20-F']
        for inx in range(len(clks)):
        # for Type in Types:
            # filterurl = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={clks[inx].strip()}&type={Type}&dateb=&owner=include&count=40'
            filterurl = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={clks[inx]}&type=10-k&dateb=2009&owner=include&count=100'
            yield scrapy.Request(url=filterurl, callback=self.parse_clk_url,
                meta = {'clk':clks[inx], 'company':companys[inx], 'Type':'10-K'})
    def next_page(self, response):
        next_pages = response.xpath('//input[@value="Next 100"]/@onclick').extract()
        if len(next_pages) > 0:
            next_p = next_pages[0].split('=',1)[1]
            yield scrapy.Request(url=f'https://www.sec.gov{next_p}'.replace("'",'').replace('"',''), callback=self.next_page,
                meta = {'clk':response.meta['clk'], 'company':response.meta['company'], 'Type':response.meta['Type']})
        yield scrapy.Request(url=response.url, callback=self.parse_clk_url,
            meta = {'clk':response.meta['clk'], 'company':response.meta['company'], 'Type':response.meta['Type']})
    def parse_clk_url(self, response):
        next_pages = response.xpath('//input[@value="Next 100"]/@onclick').extract()
        dates = response.xpath('//table/tr/td[4]/text()').extract()[2:]
        clk = response.meta['clk']
        company = response.meta['company']
        Type = response.meta['Type']
        clk_url = response.url
        if dates:
            document_urls = response.xpath('//table/tr/td[2]/a[1]/@href').extract()
            for inx in range(len(dates)):
                if dates[inx][:4] == '2009':
                    break
                documents = f'https://www.sec.gov{document_urls[inx]}'.replace('/ix?doc=','')
                yield scrapy.Request(url=documents, callback=self.parse_year_url,
                        meta = {'clk':clk,'Type':Type,'company':company,'clk_url':clk_url,'date':dates[inx]})
        if len(next_pages) > 0:
            next_p = next_pages[0].split('=',1)[1]
            yield scrapy.Request(url=f'https://www.sec.gov{next_p}'.replace("'",'').replace('"',''), callback=self.parse_clk_url,
                meta = {'clk':response.meta['clk'], 'company':response.meta['company'], 'Type':response.meta['Type']})
    def parse_year_url(self, response):
        types = response.xpath('//table/tr/td[4]/text()').extract()
        Documents = response.xpath('//table/tr/td[3]/a/@href').extract()
        clk = response.meta['clk']
        clk_url = response.meta['clk_url']
        date = response.meta['date']
        company = response.meta['company']
        Type = response.meta['Type']
        ten_year_url = response.url
        for inx in range(len(types)):
            if types[inx] == '10-K':
                pageurl = f'https://www.sec.gov{Documents[inx]}'.replace('/ix?doc=','')
                yield scrapy.Request(url=pageurl, callback=self.parse_bodys, encoding='utf-8-sig',
                        meta = {'clk':clk,'Type':Type,'company':company,'clk_url':clk_url,'date':date,'ten_year_url':ten_year_url})
    def parse_bodys(self, response):
        item = EdgarItem()
        item['clk'] = response.meta['clk']
        item['clk_url'] = response.meta['clk_url']
        item['ten_year_url'] = response.meta['ten_year_url']
        item['date'] = response.meta['date']
        item['company'] = response.meta['company']
        item['type'] = response.meta['Type']
        url = response.url
        item['body_url'] = url
        if '.pdf' in url:
            item['seven_body'] = 'pdf format'
            item['is_item_seven'] = 'pdf format'
            yield item
        else:
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
            c = str.maketrans("\x92-\x94-\x93-\x96-\x97", '" " " " "')
            item_seven_no_ints = [' '.join(element.split()).translate(c).replace('Table of Contents','') for element in item_seven
                                  if re.match(r'^-?\d+(?:\.\d+)?$', element.strip()) is None]
            # Remove blank list values
            item_seven_final = list(filter(None, item_seven_no_ints))
            is_item_seven = 1 if len(item_seven_final) < 1500 else 0
            # item['seven_body'] = ''.join(item_seven_final)
            seven_body = ''.join(item_seven_final)
            seven_body_number = math.ceil(len(seven_body)/30000)
            item['seven_body_number'] = seven_body_number
            datas = []
            for i in range(seven_body_number):
                datas.append(seven_body[i*30000:30000*(i+1)])
            try:
                item['seven_body_1'] = datas[0]
            except:
                item['seven_body_1'] = ''
            try:
                item['seven_body_2'] = datas[1]
            except:
                item['seven_body_2'] = ''
            try:
                item['seven_body_3'] = datas[2]
            except:
                item['seven_body_3'] = ''
            try:
                item['seven_body_4'] = datas[3]
            except:
                item['seven_body_4'] = ''
            try:
                item['seven_body_5'] = datas[4]
            except:
                item['seven_body_5'] = ''
            try:
                item['seven_body_6'] = datas[5]
            except:
                item['seven_body_6'] = ''
            try:
                item['seven_body_7'] = datas[6]
            except:
                item['seven_body_7'] = ''
            try:
                item['seven_body_8'] = datas[7]
            except:
                item['seven_body_8'] = ''
            item['is_item_seven'] = is_item_seven
            yield item

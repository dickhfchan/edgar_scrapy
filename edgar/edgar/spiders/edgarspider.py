# -*- coding: utf-8 -*-
import scrapy
import re
from edgar.items import EdgarItem
from scrapy.shell import inspect_response


class EdgarspiderSpider(scrapy.Spider):
    name = 'edgarspider'
    # allowed_domains = [''https://en.wikipedia.org/']
    start_urls = ['https://en.wikipedia.org/wiki/List_of_S%26P_500_companies']
    custom_settings = {
        'ITEM_PIPELINES': {
                'edgar.pipelines.Edgarxlsxspider': 400
                }
        }

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
        if url.endswith('pdf'):
            item['seven_body'] = 'pdf format'
            yield item
        else:
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
            c = str.maketrans("\x92-\x94-\x93-\x96-\x97", '" " " " "')
            item_seven_no_ints = [' '.join(element.split()).translate(c).replace('Table of Contents','') for element in item_seven
                                  if re.match(r'^-?\d+(?:\.\d+)?$', element.strip()) is None]
            # Remove blank list values
            item_seven_final = list(filter(None, item_seven_no_ints))
            item['seven_body'] = ''.join(item_seven_final)
            yield item
#caiyi
    # def parse_year_url(self, response):
    #     # get body all types
    #     types = response.xpath('//table/tr/td[4]/text()').extract()
    #     # get all urls
    #     Documents = response.xpath('//table/tr/td[3]/a/@href').extract()
    #     clk = response.meta['clk']
    #     clk_url = response.meta['clk_url']
    #     date = response.meta['date']
    #     ten_year_url = response.url
    #     for inx in range(len(types)):
    #         # get type is 10-k the url
    #         if types[inx] == '10-K':
    #             pageurl = f'https://www.sec.gov{Documents[inx]}'
    #             yield scrapy.Request(url=pageurl, callback=self.parse_bodys,meta = {'clk':clk,'clk_url':clk_url,'date':date,'ten_year_url':ten_year_url})
    # def parse_bodys(self, response):
    #     item = EdgarItem()
    #     item['clk'] = response.meta['clk']
    #     item['clk_url'] = response.meta['clk_url']
    #     item['ten_year_url'] = response.meta['ten_year_url']
    #     item['date'] = response.meta['date']
    #     url = response.url
    #     # Judge url end is pdf format,Do not handle such pdf's url
    #     if url.endswith('pdf'):
    #         item['body_url'] = url
    #         item['seven_body'] = 'Non pdf'
    #         item['sevenA_body'] = 'Non pdf'
    #         yield item
    #     else:
    #         item['body_url'] = url
    #         # re Match all html tags,eg:<a></a>
    #         re_h=re.compile('</?\w+[^>]*>')
    #         # re Filter all html tags
    #         bodys = re_h.sub(' ',response.text)
    #         # re Match all html comment tags,eg:<!--123-->
    #         re_comment=re.compile('<!--[^>]*-->')
    #         # re Filter all html comment tags
    #         body = re_comment.sub('',bodys)
    #         # re Filter all illegal characters
    #         s = r'(\n|\r|\xa0|/s/|\t|&nbsp;|Table of Contents|&#\d*;)'
    #         content = re.sub(s,' ',body)
    #         # re Match item 7 content
    #         seven = re.findall('(Item 7\.[\s\S]+?)Item 7A\.',content,re.I)
    #         # re Match item 7A content
    #         sevenA = re.findall('(Item 7A\.[\s\S]+?)Item 8\.',content,re.I)
    #         item['seven_body'] = seven[0] if len(seven) == 1 else seven[1]
    #         item['sevenA_body'] = sevenA[0] if len(sevenA) == 1 else sevenA[1]
    #         yield item

# -*- coding: utf-8 -*-
import scrapy
import re
from edgar.items import EdgarItem
from scrapy.shell import inspect_response


class EdgarspiderSpider(scrapy.Spider):
    name = 'edgarspider'
    # allowed_domains = ['https://en.wikipedia.org/wiki/List_of_S%26P_500_companies']
    start_urls = ['https://en.wikipedia.org/wiki/List_of_S%26P_500_companies']
    custom_settings = {
        'ITEM_PIPELINES': {
                'edgar.pipelines.EdgarPipeline': 400
                }
        }
              
    def parse(self, response):
        # get clks datas
        clks = response.xpath('//*[@id="constituents"]/tbody/tr/td[8]/text()').extract()
        for clk in clks:
            # get clk and filter 10-k url
            filterurl = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={clk.strip()}&type=10-K&dateb=&owner=include&count=40'
            yield scrapy.Request(url=filterurl, callback=self.parse_clk_url,meta = {'clk':clk})
    def parse_clk_url(self, response):
        # get dates
        dates = response.xpath('//table/tr/td[4]/text()').extract()[2:]
        # get the url corresponding to the time
        document_urls = response.xpath('//table/tr/td[2]/a[1]/@href').extract()
        clk = response.meta['clk']
        clk_url = response.url
        for inx in range(len(dates)):
            # As of 2009
            if dates[inx][:4] == '2009':
                break
            documents = f'https://www.sec.gov{document_urls[inx]}'
            yield scrapy.Request(url=documents, callback=self.parse_year_url,meta = {'clk':clk,'clk_url':clk_url,'date':dates[inx]})
    def parse_year_url(self, response):
        # get body all types
        types = response.xpath('//table/tr/td[4]/text()').extract()
        # get all urls
        Documents = response.xpath('//table/tr/td[3]/a/@href').extract()
        clk = response.meta['clk']
        clk_url = response.meta['clk_url']
        date = response.meta['date']
        ten_year_url = response.url
        for inx in range(len(types)):
            # get type is 10-k the url
            if types[inx] == '10-K':
                pageurl = f'https://www.sec.gov{Documents[inx]}'
                yield scrapy.Request(url=pageurl, callback=self.parse_bodys,meta = {'clk':clk,'clk_url':clk_url,'date':date,'ten_year_url':ten_year_url})
    def parse_bodys(self, response):
        item = EdgarItem()
        item['clk'] = response.meta['clk']
        item['clk_url'] = response.meta['clk_url']
        item['ten_year_url'] = response.meta['ten_year_url']
        item['date'] = response.meta['date']
        url = response.url
        # Judge url end is pdf format,Do not handle such pdf's url
        if url.endswith('pdf'):
            item['body_url'] = url
            item['seven_body'] = 'Non pdf'
            item['sevenA_body'] = 'Non pdf'
            yield item
        else:
            item['body_url'] = url
            # re Match all html tags,eg:<a></a>
            re_h=re.compile('</?\w+[^>]*>')
            # re Filter all html tags
            bodys = re_h.sub(' ',response.text)
            # re Match all html comment tags,eg:<!--123-->
            re_comment=re.compile('<!--[^>]*-->')
            # re Filter all html comment tags
            body = re_comment.sub('',bodys)
            # re Filter all illegal characters
            s = r'(\n|\r|\xa0|/s/|\t|&nbsp;|Table of Contents|&#\d*;)'
            content = re.sub(s,' ',body)
            # re Match item 7 content
            seven = re.findall('(Item 7\.[\s\S]+?)Item 7A\.',content,re.I)
            # re Match item 7A content
            sevenA = re.findall('(Item 7A\.[\s\S]+?)Item 8\.',content,re.I)
            item['seven_body'] = seven[0] if len(seven) == 1 else seven[1]
            item['sevenA_body'] = sevenA[0] if len(sevenA) == 1 else sevenA[1]
            yield item

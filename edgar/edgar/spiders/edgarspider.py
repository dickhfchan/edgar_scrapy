# -*- coding: utf-8 -*-
import scrapy
import re
from edgar.items import EdgarItem


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
        clks = response.xpath('//*[@id="constituents"]/tbody/tr/td[8]/text()').extract()
        for clk in clks:
            filterurl = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={clk.strip()}&type=10-K&dateb=&owner=include&count=40'
            yield scrapy.Request(url=filterurl, callback=self.parse_clk_url,meta = {'clk':clk})
    def parse_clk_url(self, response):
        dates = response.xpath('//table/tr/td[4]/text()').extract()[2:]
        document_urls = response.xpath('//table/tr/td[2]/a[1]/@href').extract()
        clk = response.meta['clk']
        clk_url = response.url
        for inx in range(len(dates)):
            if dates[inx][:4] == '2009':
                break
            documents = f'https://www.sec.gov{document_urls[inx]}'
            yield scrapy.Request(url=documents, callback=self.parse_year_url,meta = {'clk':clk,'clk_url':clk_url,'filing_date':dates[inx]})
    def parse_year_url(self, response):
        types = response.xpath('//table/tr/td[4]/text()').extract()
        Documents = response.xpath('//table/tr/td[3]/a/@href').extract()
        clk = response.meta['clk']
        clk_url = response.meta['clk_url']
        filing_date = response.meta['filing_date']
        ten_year_url = response.url
        for inx in range(len(types)):
            if types[inx] == '10-K':
                pageurl = f'https://www.sec.gov{Documents[inx]}'
                yield scrapy.Request(url=pageurl, callback=self.parse_bodys,meta = {'clk':clk,'clk_url':clk_url,'filing_date':filing_date,'ten_year_url':ten_year_url})
    def parse_bodys(self, response):
        item = EdgarItem()
        item['clk'] = response.meta['clk']
        item['clk_url'] = response.meta['clk_url']
        item['ten_year_url'] = response.meta['ten_year_url']
        item['filing_date'] = response.meta['filing_date']
        item['body_url'] = response.url
        re_h=re.compile('</?\w+[^>]*>')
        bodys = re_h.sub(' ',response.text)
        re_comment=re.compile('<!--[^>]*-->') 
        body = re_comment.sub('',bodys)
        s = r'(\n|\r|\xa0|/s/|\t|&nbsp;|Table of Contents|&#\d*;)'
        content = re.sub(s,' ',body)
        seven = re.findall('(Item 7\.[\s\S]+?)Item 7A\.',content,re.I)
        sevenA = re.findall('(Item 7A\.[\s\S]+?)Item 8\.',content,re.I)
        item['seven_body'] = seven[0] if len(seven) == 1 else seven[1]
        item['sevenA_body'] = sevenA[0] if len(sevenA) == 1 else sevenA[1]
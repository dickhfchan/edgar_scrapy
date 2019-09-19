# -*- coding: utf-8 -*-
import scrapy
import re
from edgar.items import EdgarItem
from scrapy.shell import inspect_response


class EdgarfetchSpider(scrapy.Spider):
    name = 'edgarfetch'
    # allowed_domains = ['https://en.wikipedia.org/wiki/List_of_S%26P_500_companies']
    start_urls = ['http://https://en.wikipedia.org/wiki/List_of_S%26P_500_companies/']
    custom_settings = {
        'ITEM_PIPELINES': {
                'edgar.pipelines.EdgarPipeline': 400
                }
        }

    def parse(self, response):
        clks = response.xpath('//*[@id="constituents"]/tbody/tr/td[8]/text()').extract()
        companys = response.xpath('//*[@id="constituents"]/tbody/tr/td[2]/a/text()').extract()
        Types = ['10-K','10-Q','20-F']
        for inx in range(len(clks)):
            for Type in Types:
                filterurl = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={clks[inx].strip()}&type={Type}&dateb=&owner=include&count=40'
                yield scrapy.Request(url=filterurl, callback=self.parse_clk_url,
                    meta = {'clk':clks[inx], 'company':companys[inx], 'Type':Type})
    def parse_clk_url(self, response):
        dates = response.xpath('//table/tr/td[4]/text()').extract()[2:]
        clk = response.meta['clk']
        company = response.meta['company']
        clk_url = response.url
        if dates:
            document_urls = response.xpath('//table/tr/td[2]/a[1]/@href').extract()
            for inx in range(len(dates)):
                if dates[inx][:4] == '2009':
                    break
                documents = f'https://www.sec.gov{document_urls[inx]}'
                yield scrapy.Request(url=documents, callback=self.parse_year_url,
                        meta = {'clk':clk,'company':company,'clk_url':clk_url,'date':dates[inx]})
        else:
            item = EdgarItem()
            item['clk'] = clk
            item['clk_url'] = clk_url
            item['company'] = company
            item['date'] = 'Non'
            item['ten_year_url'] = 'Non'
            item['body_url'] = 'Non'
            item['body'] = 'Non'
            yield item
    def parse_year_url(self, response):
        types = response.xpath('//table/tr/td[4]/text()').extract()
        Documents = response.xpath('//table/tr/td[3]/a/@href').extract()
        clk = response.meta['clk']
        clk_url = response.meta['clk_url']
        date = response.meta['date']
        company = response.meta['company']
        ten_year_url = response.url
        for inx in range(len(types)):
            if types[inx] == '10-K':
                pageurl = f'https://www.sec.gov{Documents[inx]}'
                yield scrapy.Request(url=pageurl, callback=self.parse_bodys,
                        meta = {'clk':clk,'company':company,'clk_url':clk_url,'date':date,'ten_year_url':ten_year_url})
    def parse_bodys(self, response):
        item = EdgarItem()
        item['clk'] = response.meta['clk']
        item['clk_url'] = response.meta['clk_url']
        item['ten_year_url'] = response.meta['ten_year_url']
        item['date'] = response.meta['date']
        item['company'] = response.meta['company']
        url = response.url
        if url.endswith('pdf'):
            item['body_url'] = url
            item['body'] = 'pdf format'
            yield item
        else:
            item['body_url'] = url
            re_h=re.compile('</?\w+[^>]*>')
            bodys = re_h.sub(' ',response.text)
            re_comment=re.compile('<!--[^>]*-->')
            body = re_comment.sub('',bodys)
            item['body'] = body
            yield item

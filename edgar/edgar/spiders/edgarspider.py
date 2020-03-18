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
        # for inx in range(len(clks)):
        # for Type in Types:
            # filterurl = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={clks[inx].strip()}&type={Type}&dateb=&owner=include&count=40'
        filterurl = f'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001058090&type=10-k&dateb=2009&owner=include&count=100'
        yield scrapy.Request(url=filterurl, callback=self.parse_clk_url,
            meta = {'clk':'0001058090', 'company':'Chipotle Mexican Grill', 'Type':'10-K'})
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
        # if len(next_pages) > 0:
        #     next_p = next_pages[0].split('=',1)[1]
        #     yield scrapy.Request(url=f'https://www.sec.gov{next_p}'.replace("'",'').replace('"',''), callback=self.parse_clk_url,
        #         meta = {'clk':response.meta['clk'], 'company':response.meta['company'], 'Type':response.meta['Type']})
        else:
            item = EdgarItem()
            item['clk'] = clk
            item['clk_url'] = clk_url
            item['company'] = company
            item['date'] = 'Non'
            item['ten_year_url'] = 'Non'
            item['body_url'] = 'Non'
            item['seven_body'] = 'Non'
            item['sevenA_body'] = 'Non'
            item['type'] = Type
            yield item
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
                yield scrapy.Request(url=pageurl, callback=self.parse_bodys,
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
            item['sevenA_body'] = 'pdf format'
            yield item
        else:
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
            item['seven_body'] = item_seven_final
            item['sevenA_body'] = 'test'
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

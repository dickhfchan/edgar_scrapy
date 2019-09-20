# -*- coding: utf-8 -*-
import scrapy
import json
from edgar.items import Hangseng

class HangsengSpider(scrapy.Spider):
    name = 'hangseng'
    # allowed_domains = ['https://www.hsi.com.hk/eng/indexes/all-indexes/industry']
    start_urls = ['https://www.hsi.com.hk/data/eng/rt/index-series/industry/constituents.do?9839']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    }
    custom_settings = {
        'ITEM_PIPELINES': {
                'edgar.pipelines.HangsengPipeline': 400
                }
        }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, headers=self.headers ,callback=self.parse)

    def parse(self, response):
        item = Hangseng()
        data = json.loads(response.body_as_unicode())
        indexSeriesList = data['indexSeriesList']
        indexList = indexSeriesList[0]['indexList']
        for indexlist in indexList:
            for constituentcontent in indexlist['constituentContent']:
                item['constituent_type'] = indexlist['indexName']
                item['code'] = constituentcontent['code']
                item['constituent_name'] = constituentcontent['constituentName']
                yield item

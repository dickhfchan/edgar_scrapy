# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class EdgarItem(scrapy.Item):
    # define the fields for your item here like:
    clk = scrapy.Field()
    clk_url = scrapy.Field()
    ten_year_url = scrapy.Field()
    body_url = scrapy.Field()
    seven_body = scrapy.Field()
    sevenA_body = scrapy.Field()
    company = scrapy.Field()
    date = scrapy.Field()
    type = scrapy.Field()
    body = scrapy.Field()


class Hangseng(scrapy.Item):
    code = scrapy.Field()
    constituent_type = scrapy.Field()
    constituent_name = scrapy.Field()


class DocumentItem(scrapy.Item):
    item_seven = scrapy.Field()
    item_sevena = scrapy.Field()

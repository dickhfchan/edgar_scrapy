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
    company = scrapy.Field()
    date = scrapy.Field()
    type = scrapy.Field()
    body = scrapy.Field()
    seven_body_number = scrapy.Field()
    seven_body_1 = scrapy.Field()
    seven_body_2 = scrapy.Field()
    seven_body_3 = scrapy.Field()
    seven_body_4 = scrapy.Field()
    seven_body_5 = scrapy.Field()
    seven_body_6 = scrapy.Field()
    seven_body_7 = scrapy.Field()
    seven_body_8 = scrapy.Field()
    is_item_seven = scrapy.Field()

class Hangseng(scrapy.Item):
    code = scrapy.Field()
    constituent_type = scrapy.Field()
    constituent_name = scrapy.Field()

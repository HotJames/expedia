# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class ExpediaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    hotel_name = Field()
    hotel_id = Field()
    display_price = Field()
    local = Field()
    available_offer = Field()
    reviews_count = Field()
    reviews_rate = Field()
    url = Field()
    room_price = Field()

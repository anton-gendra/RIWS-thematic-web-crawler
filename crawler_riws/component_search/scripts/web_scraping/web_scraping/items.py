# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Component(scrapy.Item):
    name = scrapy.Field()
    vendor = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    weight = scrapy.Field()
    category = scrapy.Field()
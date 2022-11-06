# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Component(scrapy.Item):
    name = scrapy.Field()
    brand = scrapy.Field()
    price = scrapy.Field()
    link = scrapy.Field()
    source = scrapy.Field()
    weight = scrapy.Field()
    height = scrapy.Field()
    width = scrapy.Field()
    category = scrapy.Field()
    storing_capacity = scrapy.Field()
    power = scrapy.Field()
    speed = scrapy.Field()
    latency = scrapy.Field()
    max_temperature = scrapy.Field()
    year = scrapy.Field()
    generation = scrapy.Field()
    rating = scrapy.Field()
    socket = scrapy.Field()
    interface = scrapy.Field()
    achitecture = scrapy.Field()
    image = scrapy.Field()
import scrapy
from scrapy.spiders import CrawlSpider, Rule, Request
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component


class GigabyteSpider(CrawlSpider):
    name = 'gigabyte-spider'
    allowed_domains = ['gigabyte.com']
    start_urls = ['https://www.gigabyte.com/']

    rules = (
        Rule(LinkExtractor(allow=[
            'Motherboard',
            'Graphics-Card',
            'Laptop',
            'Monitor',
            'Desktops',
            'PC-Peripherals',
            'Keyboard',
            'Mouse',
            'Headset',
            'PC-Components',
            'PC-Case',
            'Power-Supply',
            'CPU-Cooler',
            'SSD',
            'Memory',
            'DIY-KIT'
        ]), callback='parse_list', follow=True),
    )

    def parse_component(self, response, component):
        yield component

    def parse_list(self, response):
        components = response.css("div.product_list_box")
        for component in components:
            name = component.css("span.product_info_Name::text").get()
            link = component.css("a.product_list_box_info_ImageLink::attr(href)").get()

            arg = {'component': Component(name=name, link=link)}
            yield response.follow(link, callback=self.parse_component, cb_kwargs=arg)
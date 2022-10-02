import scrapy
from scrapy.spiders import CrawlSpider, Rule
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
        ]), callback='parse_component'),
    )

    def parse_component(self, response):
        components = response.css("div.product_list_box")
        for component in components:
            name = component.css("span.product_info_Name::text").get()
            yield Component(name=name)
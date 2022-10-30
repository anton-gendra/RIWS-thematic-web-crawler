import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component


class CoolmodSpider(CrawlSpider):
    name = 'coolmod-spider'
    allowed_domains = ['coolmod.com']
    start_urls = ['https://www.coolmod.com/']

    rules = (
        Rule(LinkExtractor(allow=[
            'componentes-pc',
            'tarjetas-graficas',
            'grabadoras-dvd-blu-ray',
            'ventiladores',
            'tarjetas-de-sonido'
        ]), callback='parse_component'),
    )

    def parse_component(self, response):
        components = response.css("div.productflex")
        for component in components:
            name = component.css("div.d-table-cell img::attr(alt)").get()
            yield Component(name=name)
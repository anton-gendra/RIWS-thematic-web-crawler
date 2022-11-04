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
        ]), callback='parse_list'),
    )

    def parse_component(self, response, component):
        yield component

    def parse_list(self, response):
        components = response.css("div.productflex")
        for component in components:
            name = component.css("div.d-table-cell img::attr(alt)").get()
            link = component.css("div.productName a::attr(href)").get()
            
            arg = {'component': Component(name=name)}
            yield response.follow(link, callback=self.parse_component, cb_kwargs=arg)
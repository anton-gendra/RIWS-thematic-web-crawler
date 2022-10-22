import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component


class WipoidSpider(CrawlSpider):
    name = 'wipoid-spider'
    allowed_domains = ['wipoid.com']
    start_urls = ['https://www.wipoid.com/']

    rules = (
        Rule(LinkExtractor(allow=[
            'procesadores',
            'placas-base',
            'ventiladores',
            'tarjetas-graficas',
            'memoria-ram',
            'refrigeracion-cpu',
            'discos-duros',
            'fuentes-alimentacion',
            'torres-cajas-carcasas',
            'grabadoras-dvd-blu-ray',
            'accesorios-caja',
            'cables-y-adaptadores'
        ]), callback='parse_component'),
    )

    def parse_component(self, response):
        components = response.css("div.item-inner")
        for component in components:
            name = component.css("a.product-name::text").get().strip()
            yield Component(name=name)
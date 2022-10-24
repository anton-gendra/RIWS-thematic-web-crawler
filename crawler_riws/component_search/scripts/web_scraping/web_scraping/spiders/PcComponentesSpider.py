import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component


class PcComponentesSpider(CrawlSpider):
    name = 'pccomponentes-spider'
    allowed_domains = ['pccomponentes.com']
    start_urls = ['https://www.pccomponentes.com/']

    rules = (
        Rule(LinkExtractor(allow=[
            'placas-base',
            'procesadores',
            'discos-duros',
            'discos-duros-ssd',
            'tarjetas-graficas',
            'memorias-ram',
            'grabadores-dvd-blu-ray',
            'multilectores',
            'tarjetas-sonido',
            'torres',
            'ventilacion',
            'fuentes-alimentacion',
            'modding',
            'capturadoras',
            'cables-internos-de-pc',
            'conectividad'
        ]), callback='parse_component'),
    )

    def parse_component(self, response):
        components = response.css("div.product-card")
        for component in components:
            name = component.css("h3.product-card__title::text").get()
            yield Component(name=name)
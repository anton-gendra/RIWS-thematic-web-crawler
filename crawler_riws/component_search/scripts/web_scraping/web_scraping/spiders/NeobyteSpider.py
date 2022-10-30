import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component


class GigabyteSpider(CrawlSpider):
    name = 'neobyte-spider'
    allowed_domains = ['neobyte.es']
    start_urls = ['https://www.neobyte.es/']

    rules = (
        Rule(LinkExtractor(allow=[
            'procesadores-107',
            'placas-base-106',
            'memorias-ram-108',
            'ventilacion-109',
            'discos-duros-110',
            'tarjetas-graficas-111',
            'cajas-de-ordenador-112',
            'fuentes-de-alimentacion-113',
            'grabadoras-dvd-blu-ray-114',
            'tarjetas-de-sonido-115',
            'capturadoras-de-video-116',
            'teclados-166',
            'ratones-168',
            'monitores-169',
            
        ]), callback='parse_component'),
    )

    def parse_component(self, response):
        components = response.css("div.js-product-miniature-wrapper")
        for component in components:
            name = component.css("span.h3.product-title a::text").get()
            yield Component(name=name)
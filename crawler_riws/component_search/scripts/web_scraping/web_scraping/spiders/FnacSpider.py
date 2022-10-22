import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component

class FnacSpider(CrawlSpider):
    name = 'fnac-spider'
    allowed_domains = ['fnac.es']
    start_urls = ['https://www.fnac.es/ordenador-PC/Componentes-de-PC/s126383#bl=MMInformatica']

    rules = (
        Rule(LinkExtractor(allow=[
            'Discos-SSD',
            'Memorias-RAM',
            'Lectores-de-CD-DVD-Blu-Ray',
            'Placas-base',
            'Tarjetas-graficas',
            'Tarjetas-de-sonido',
            'Procesadores',
            'Ventiladores-internos-PC'
        ]), callback='parse_component'),
    )

    def parse_component(self, response):
        components = response.css("div.Aticle-item")
        for component in components:
            name = component.css("a::text").get()
            yield Component(name=name)
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component


class AlternateSpider(CrawlSpider):
    name = 'alternate-spider'
    allowed_domains = ['alternate.es']
    start_urls = ['https://www.alternate.es/']

    rules = (
        Rule(LinkExtractor(allow=[
            'Cajas-de-PC',
            'Discos-duros',
            'Disipadores-de-CPU',
            'Dispositivos-de-discos',
            'Fuentes-de-alimentación',
            'Kits-de-actualización-de-PC',
            'Memoria-RAM',
            'Placas-base',
            'Procesadores',
            'Refrigeración-líquida',
            'Tarjetas-Capture',
            'Tarjetas-de-red',
            'Tarjetas-de-sonido',
            'Tarjetas-gráficas',
            'Ventiladores-de-caja-de-PC'
        ]), callback='parse_component'),
    )

    def parse_component(self, response):
        components = response.css("div.container.my-3")
        for component in components:
            name = component.css("div.product-name::text").get()
            yield Component(name=name)
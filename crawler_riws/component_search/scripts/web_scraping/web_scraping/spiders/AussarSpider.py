import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component


class AussarSpider(CrawlSpider):
    name = 'aussar-spider'
    allowed_domains = ['aussar.es']
    start_urls = ['https://www.aussar.es/']

    rules = (
        Rule(LinkExtractor(allow=[
            'procesadores',
            'placas-base',
            'memoria',
            'refrigeracion',
            'almacenamiento',
            'opticos',
            'tarjetas-graficas',
            'perifericos/lectores-de-tarjetas',
            'sonido',
            'cajas',
            'alimentacion/fuentes',
            'alimentacion/sai',
            'refrigeracion/ventiladores-caja-cpu',
            'redes/tarjetas-de-red-y-wifi',
            'sistemas-operativos'
        ]), callback='parse_component'),
    )

    def parse_component(self, response):
        components = response.css("h3.product-title")
        for component in components:
            name = component.css("a::text").get()
            yield Component(name=name)
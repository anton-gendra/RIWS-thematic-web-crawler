import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component


class PcMontajesSpider(CrawlSpider):
    name = 'pcmontajes-spider'
    allowed_domains = ['pcmontajes.com']
    start_urls = ['https://www.pcmontajes.com/componentes']

    rules = (
        Rule(LinkExtractor(allow=[
            '7-componentes-unidades-opticas',
            '11-componentes-refrigeracion',
            '12-disipadores-para-cpu',
            '329-componentes-memorias',
            '17-componentes-tarjetas-graficas',
            '38-componentes-discos-duros-discos-duros-internos-3-5',
            '63-componentes-discos-duros-discos-duros-ssd',
            '33-componentes-fuentes-de-alimentacion',
            '36-componentes-placas-base',
            '47-componentes-cajas-pc',
            '50-componentes-procesadores',
            '55-componentes-lectores-de-tarjetas',
            '89-conectividad',
            '115-componentes-tarjetas-de-sonido'
        ]), callback='parse_component'),
    )

    def parse_component(self, response):
        components = response.css("div.ajax_block_product")
        for component in components:
            name = component.css("a.product-name::text").get().strip()
            yield Component(name=name)
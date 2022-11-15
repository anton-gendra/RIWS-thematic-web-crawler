from gc import callbacks
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component

CATEGORIES = {
    "Procesadores": "processor",
    "Tarjetas Gráficas": "graphic-card",
    "TARJETAS": "net-card",
    "Sonido": "sound-card",
    "Placas Base": "motherboard",
    "Refrigeración": "fan",
    "Memoria": "RAM",
    "SSD": "SSD",
    "DISCOS HDD": "HDD",
    "FUENTES": "power-source",
    "Cajas": "tower"
}

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
            'almacenamiento/ssd',
            'almacenamiento/discos-hdd'
            'tarjetas-graficas',
            'sonido',
            'cajas',
            'alimentacion/fuentes',
            'redes/tarjetas-de-red-y-wifi'
        ], 
        deny=[
            'intel',
            'amd',
            'AMD',
            'ddr4',
            'ddr5',
            'nvidia',
            'profesionales',
            'liquida',
            'aire'
        ]), callback='parse_list'),
    )

    def parse_component(self, response, component):
        component['source'] = 'aussar'
        price = response.css("span.current-price-value::attr(content)").get()
        component['price'] = price
        brand = response.css("div.product-manufacturer a::text").get()
        component['brand'] = brand
        
        specsList = response.css("div.product-description p::text").get()

        yield component

    def parse_list(self, response):
        category = response.css("h1.category-name::text").get()
        try:
            category = CATEGORIES[category]
            components = response.css("div.ajax_block_product")
            for component in components:
                name = component.css("h3.product-title a::text").get()
                link = component.css("h3.product-title a::attr(href)").get()
                image = component.css("img.img-fluid::attr(src)").get()

                arg = {'component': Component(name=name, category=category, link=link, image=image)}
                yield response.follow(link, callback=self.parse_component, cb_kwargs=arg)
        except KeyError:
            pass

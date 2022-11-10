from gc import callbacks
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
        ]), callback='parse_list'),
    )

    def parse_component(self, response, component):
        price = response.css("span.current-price-value::attr(content)").get()
        brand = response.css("div.product-manufacturer a::text").get()
        source = 'aussar'
        yield component

    def parse_list(self, response):
        category = response.css("h1.category-name::text").get()

        components = response.css("div.ajax_block_product")
        for component in components:
            name = component.css("h3.product-title a::text").get()
            link = component.css("h3.product-title a::attr(href)").get()
            image = component.css("img.img-fluid::attr(src)").get()

            arg = {'component': Component(name=name, category=category, link=link, image=image)}
            yield response.follow(link, callback=self.parse_component, cb_kwargs=arg)
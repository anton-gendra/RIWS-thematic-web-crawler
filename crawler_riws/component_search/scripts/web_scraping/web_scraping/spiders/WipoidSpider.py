import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component


CATEGORIES = {
    "Procesadores": "processor",
    "Tarjetas Gráficas": "graphic-card",
    "tarjetas-de-sonido": "sound-card",
    "Placas Base": "motherboard",
    "Refrigeración CPU": "fan",
    "Memoria RAM": "RAM",
    "Discos Duros": "HDD",
    "Fuentes Alimentación": "power-source",
    "Torres/Cajas": "tower"
}


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
            'refrigeracion-cpu'
            'discos-duros',
            'fuentes-alimentacion',
            'torres-cajas-carcasas'
        ]), callback='parse_list'),
    )

    def parse_component(self, response, component):
        component['source'] = 'wipoid'
        productLabels = response.css("div.prd-reference a::text")[-1].get()
        brand = productLabels[1] if (len(productLabels) == 2) else None
        component['brand'] = brand
        price = response.css("div.our_price_display span::text").get()
        component['price'] = price
        specsList = response.css("section.page-product-box p::text").getall()

        specsListLen = len(specsList)
        #print(specsList)
        for i,e in enumerate(specsList):
            #print('objetooooooooooooo', e)
            if ('gráfico' in e.lower()) or ('arquitectura' in e.lower()):
                component['achitecture'] = None if ((i+1) > specsListLen) else specsList[i+1]
            elif 'speed' in e.lower():
                component['speed'] = None if ((i+1) > specsListLen) else specsList[i+1]
            #elif 'cuda' in e.lower():
            #    component['cuda'] = None if ((i+1) > specsList) else specsList[i+1]
            elif ('tamaño de la memoria' in e.lower()) or ('memoria de video' in e.lower()) or ('capacidad' in e.lower()):
                component['storing_capacity'] = None if ((i+1) > specsListLen) else specsList[i+1]
            elif ('tamaño de la tarjeta' in e.lower()) or ('dimensiones' in e.lower()):
                component['height'] = e
                component['width'] = e
            elif ('peso' in e.lower()):
                component['weight'] = None if ((i+1) > specsListLen) else specsList[i+1]
            elif ('fuente' in e.lower()) or ('tdp' in e.lower()) or ('salida total' in e.lower()):
                component['power'] = None if ((i+1) > specsListLen) else specsList[i+1]
            elif ('temperatura' in e.lower()) or ('temp. max' in e.lower()):
                component['max_temperature'] = None if ((i+1) > specsListLen) else specsList[i+1]
            elif ('número de procesador' in e.lower()):
                component['generation'] = None if ((i+1) > specsListLen) else specsList[i+1]
            elif ('interfaz' in e.lower()):
                component['interface'] = None if ((i+1) > specsListLen) else specsList[i+1]
            elif ('latencia' in e.lower()):
                component['latency'] = None if ((i+1) > specsListLen) else specsList[i+1]
            elif ('socket' in e.lower()):
                component['socket'] = e
            
        yield component

    def parse_list(self, response):
        category = response.css("h1.category-name::text").get().strip()
        try:
            print(category, response.url)
            category = CATEGORIES[category]
            print('CATEGORYYYYYYYYYY', category, response.url)
            components = response.css("div.item-inner")
            for component in components:
                name = component.css("a.product-name::text").get().strip()
                if ('ssd' in name.lower()):
                    category = 'SSD'
                link = component.css("div.item-title a::attr(href)").get()
                image = component.css("img.replace-2x::attr(src)").get()

                arg = {'component': Component(name=name, category=category, link=link, image=image)}
                yield response.follow(link, callback=self.parse_component, cb_kwargs=arg)
        except KeyError:
            pass

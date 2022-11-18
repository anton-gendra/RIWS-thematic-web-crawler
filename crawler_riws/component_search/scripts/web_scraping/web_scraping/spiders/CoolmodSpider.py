import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component
from crawler_riws.component_search.scripts.web_scraping.web_scraping.spiders.utils.utils import match_brand

import re


CATEGORIES = {
    "componentes-pc-procesadores": "processor",
    "tarjetas-graficas": "graphic-card",
    "componentes-pc-adaptadores-red": "net-card",
    "tarjetas-de-sonido": "sound-card",
    "componentes-pc-placas-base": "motherboard",
    "ventiladores": "fan",
    "componentes-pc-memorias-ram": "RAM",
    "componentes-pc-discos-ssd": "SSD",
    "componentes-pc-discos-hdd": "HDD",
    "componentes-pc-fuentes-alimentacion": "power-source",
    "componentes-pc-torres-cajas": "tower",
    "componentes-pc-tarjetas-pci": "PCI"
}


class CoolmodSpider(CrawlSpider):
    name = 'coolmod-spider'
    allowed_domains = ['coolmod.com']
    start_urls = ['https://www.coolmod.com/']

    rules = (
        Rule(LinkExtractor(allow=[
            'componentes-pc',
            'tarjetas-graficas',
            'grabadoras-dvd-blu-ray',
            'ventiladores',
            'tarjetas-de-sonido'
        ]), callback='parse_list'),
    )

    def _format_dimension(self, value):
        value = value.lower().replace('mm', '').strip()
        if 'cm' in value.lower():
            value.replace('cm', '').strip()
            value = f"{float(value) * 100}"

        return value

    def _format_weight(self, value):
        value = value.lower().replace('kg', '').strip()
        if 'mg' in value.lower():
            value.replace('mg', '').strip()
            value = f"{float(value) / 1000}"

        return value



    def _parse_characteristic(self, name, value, component):
        if 'dimen' in name.lower():
            dimensions = value.lower().split('x')
            component['height'] = float(re.sub('[áéíóúa-z:()]', '', dimensions[2].lower()))
            component['width'] = float(re.sub('[áéíóúa-z:()]', '', dimensions[1].lower()))

        elif 'potencia' in name.lower():
            component['power'] = int(re.sub('[áéíóúa-z:()]', '', value.lower()))

        elif 'interfa' in name.lower():
            component['socket'] = value

        elif 'storage' in name.lower() or 'capacidad' in name.lower():
            component['storing_capacity'] = int(re.sub('[áéíóúa-z:()]', '', value.lower()))

        elif 'peso' in name.lower() or 'weig' in name.lower():
            component['weight'] = float(re.sub('[áéíóúa-z:()]', '', value.lower()))

        elif 'frequ' in name.lower() or 'frecuen' in name.lower() or 'reloj' in name.lower():
            component['speed'] = float(re.sub('[áéíóúa-z:()]', '', value.lower()))

        elif 'anchu' in name.lower():
            component['width'] = float(re.sub('[áéíóúa-z:()]', '', value.lower()))

        elif 'altur' in name.lower():
            component['height'] = float(re.sub('[áéíóúa-z:()]', '', value.lower()))

        elif 'socket' in name.lower():
            component['socket'] = value

        elif 'temp' in name.lower():
            component['max_temperature'] = int(re.sub('[áéíóúºªa-z:()]', '', value.lower()))

        elif 'núcle' in name.lower():
            component['cores'] = value

        elif 'hilo' in name.lower():
            component['threads'] = value

        elif 'caché' in name.lower():
            component['storing_capacity'] = int(re.sub('[áéíóúa-z:()]', '', value.lower()))

        elif 'tipo de memoria' in name.lower() or 'tipo de dispositivo' in name.lower():
            component['type'] = value



        return component

    def parse_component(self, response, component):
        component['link'] = response.url

        rows = response.css("tr")
        if not rows: 
            uls = response.css("ul")
            for ul in uls:
                lis = ul.css("li::text")
                for li in lis:
                    try:
                        spec_name, spec_value = li.root.split(':')
                        component = self._parse_characteristic(spec_name, spec_value, component)
                    
                    except ValueError:
                        continue

        else:
            for row in rows:
                cells = row.css("td::text")
                try:
                    spec_name = cells[0].root
                    spec_value = cells[1].root
                
                except IndexError:
                    continue

                component = self._parse_characteristic(spec_name, spec_value, component)


        yield component

    def parse_list(self, response):
        components = response.css("div.productflex")
        for component in components:
            name = component.css("div.d-table-cell img::attr(alt)").get()
            brand = match_brand(name)
            image_src = component.css("div.d-table-cell img::attr(src)").get()
            link = component.css("div.productName a::attr(href)").get()
            price = component.css("span.pricecontent::text").get()
            price = float(price.replace('.', '').replace(',', '.')) if price != ' ' and price else None
            try:
                category = CATEGORIES[response.url.split('/')[3]]
            
            except KeyError:
                continue

            if "ssd" in name.lower():
                category = 'SSD'

            arg = {'component': Component(name=name, category=category, image=image_src, price=price, brand=brand, source='Coolmod')}
            yield response.follow(link, callback=self.parse_component, cb_kwargs=arg)
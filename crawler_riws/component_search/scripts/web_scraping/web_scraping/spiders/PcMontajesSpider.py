import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component

CATEGORIES = {
    "Procesadores": "processor",
    "conectividad": "net-card",
    "Tarjetas de sonido": "sound-card",
    "Placas base": "motherboard",
    "Disipadores para CPU": "fan",
    "Memorias RAM": "RAM",
    "Discos duros internos 3.5": "HDD",
    "Fuentes de alimentacion": "power-source",
    "Cajas pc": "tower",
}

class PcMontajesSpider(CrawlSpider):
    name = 'pcmontajes-spider'
    allowed_domains = ['pcmontajes.com']
    start_urls = ['https://www.pcmontajes.com/componentes']

    rules = (
        Rule(LinkExtractor(allow=[
            '12-disipadores-para-cpu',
            '329-componentes-memorias',
            '38-componentes-discos-duros-discos-duros-internos-3-5',
            '33-componentes-fuentes-de-alimentacion',
            '36-componentes-placas-base',
            '47-componentes-cajas-pc',
            '50-componentes-procesadores',
            '89-conectividad',
            '115-componentes-tarjetas-de-sonido'
        ]), callback='parse_list'),
    )

    def parse_component(self, response, component):
        brand = response.css('span[itemprop="brand"] span::attr(content)').get()
        component['brand'] = brand

        price = response.css('div.our_price_display meta[itemprop="price"]::attr(content)').get()
        component['price'] = price

        component['source'] = "pcmontajes"

        rows = response.css('table.table-data-sheet tr')
        for row in rows:
            cells = row.css('td')
            if (cells[0].root.text == 'Peso'):
                component['weight'] = cells[1].root.text

            elif (cells[0].root.text == 'Altura'):
                component['height'] = cells[1].root.text

            elif (cells[0].root.text == 'Ancho'):
                component['width'] = cells[1].root.text

            elif ((cells[0].root.text == 'Memoria máxima') or (cells[0].root.text == 'Memoria interna máxima') or ('Memoria máxima' in cells[0].root.text) or (cells[0].root.text == 'Capacidad del HDD') or (cells[0].root.text == 'Memoria interna')):
                component['storing_capacity'] = cells[1].root.text

            elif ((cells[0].root.text == 'Potencia de diseño térmico (TDP)') or (cells[0].root.text == 'Intervalo de temperatura operativa') or (cells[0].root.text == 'Potencia total') or (cells[0].root.text == 'Voltaje de memoria')):
                component['power'] = cells[1].root.text

            elif ((cells[0].root.text == 'Frecuencia base del procesador') or (cells[0].root.text == 'WLAN velocidad de transferencia de datos, soportada') or (cells[0].root.text == 'Consumo energético') or (cells[0].root.text == 'Velocidad de rotación del HDD') or (cells[0].root.text == 'Velocidad de memoria del reloj')):
                component['speed'] = cells[1].root.text

            elif (cells[0].root.text == 'Frecuencia de entrada AC') or (cells[0].root.text == 'Latencia CAS'):
                component['latency'] = cells[1].root.text

            elif (cells[0].root.text == 'Intersección T'):
                component['max_temperature'] = cells[1].root.text

            elif (cells[0].root.text == 'Generación del procesador'):
                component['generation'] = cells[1].root.text

            elif (cells[0].root.text == 'Socket de procesador'):
                component['socket'] = cells[1].root.text

            elif ((cells[0].root.text == 'Interfaz') or (cells[0].root.text == 'Tipo de interfaz')):
                component['interface'] = cells[1].root.text

        yield component

    def parse_list(self, response):
        components = response.css("div.ajax_block_product")
        for component in components:
            name = component.css("a.product-name::text").get().strip()
            link = component.css("div.product-meta a::attr(href)").get()
            img = component.css("img.replace-2x::attr(src)").get()
            try:
                category = CATEGORIES[response.css("span.cat-name::text").get().strip().replace("\"", "") if response.css("span.cat-name::text").get() else None]
            except KeyError:
                continue
            arg = {'component': Component(name=name, category=category, link=link, image = img)}
            yield response.follow(link, callback = self.parse_component, cb_kwargs = arg)
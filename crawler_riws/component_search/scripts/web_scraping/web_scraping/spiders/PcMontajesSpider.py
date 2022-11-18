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
    "Discos duros ssd": "SSD",
    "Tarjetas gráficas": "graphic-card",
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
            '63-componentes-discos-duros-discos-duros-ssd',
            '17-componentes-tarjetas-graficas',
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
                peso = cells[1].root.text.split(' ')[0]
                component['weight'] = float(peso.replace(',', '.'))


            elif (cells[0].root.text == 'Altura'):
                altura = cells[1].root.text.split(' ')[0]
                component['height'] = float(altura.replace(',', '.'))


            elif (cells[0].root.text == 'Ancho'):
                ancho = cells[1].root.text.split(' ')[0]
                component['width'] = float(ancho.replace(',', '.'))


            elif ((cells[0].root.text == 'Memoria máxima') or (cells[0].root.text == 'Memoria interna máxima') or ('Memoria máxima' in cells[0].root.text) or (cells[0].root.text == 'Capacidad del HDD') or (cells[0].root.text == 'Memoria interna') or (cells[0].root.text == 'SDD, capacidad')):
                memoria = cells[1].root.text.split(' ')[0]
                component['storing_capacity'] = float(memoria.replace(',', '.'))


            elif ((cells[0].root.text == 'Potencia de diseño térmico (TDP)') or (cells[0].root.text == 'Potencia total') or (cells[0].root.text == 'Voltaje de memoria') or (cells[0].root.text == 'Suministro de energía al sistema mínimo') or (cells[0].root.text == 'Consumo energético')):
                power = cells[1].root.text.split(' ')[0]
                if (len(power) < 4):
                    power = float(power.replace(',', '.'))
                else:
                    power = float(power.split(',')[0].replace(',', '.'))
                component['power'] = power


            elif ((cells[0].root.text == 'Frecuencia base del procesador') or (cells[0].root.text == 'WLAN velocidad de transferencia de datos, soportada') or (cells[0].root.text == 'Velocidad de rotación del HDD') or (cells[0].root.text == 'Velocidad de memoria del reloj') or (cells[0].root.text == 'Velocidad de lectura')):
                speed = cells[1].root.text.split(' ')[0]
                component['speed'] = float(speed.replace(',', '.'))


            elif (cells[0].root.text == 'Frecuencia de entrada AC') or (cells[0].root.text == 'Latencia CAS'):
                latencia = cells[1].root.text.split(' ')[0]
                if ('/' in latencia):
                    latencia = float(latencia.split('/')[0])
                else:
                    latencia = float(latencia.replace(',', '.'))
                component['latency'] = latencia


            elif (cells[0].root.text == 'Intersección T'):
                temperature = cells[1].root.text.split(' ')[0]
                component['max_temperature'] = float(temperature.replace(',', '.'))


            elif (cells[0].root.text == 'Generación del procesador'):
                generation = cells[1].root.text.split(' ')
                for g in generation:
                    if ('ma' in g):
                        component['generation'] = g.replace('ma', '')
                        break


            elif (cells[0].root.text == 'Socket de procesador'):
                component['socket'] = cells[1].root.text

            elif ((cells[0].root.text == 'Interfaz') or (cells[0].root.text == 'Tipo de interfaz')):
                component['interface'] = cells[1].root.text

            elif ((cells[0].root.text == 'Número de núcleos de procesador') or (cells[0].root.text == 'Núcleos CUDA')):
                component['cores'] = cells[1].root.text

            elif ((cells[0].root.text == 'Número de hilos de ejecución')):
                component['threads'] = cells[1].root.text

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
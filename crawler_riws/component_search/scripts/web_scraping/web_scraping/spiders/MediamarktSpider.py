import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component
from crawler_riws.component_search.scripts.web_scraping.web_scraping.spiders.utils.utils import match_brand


CATEGORIES = {
    "Procesadores": "processor",
    "Tarjetas Gráficas": "graphic-card",
    "Tarjetas de Red": "net-card",
    "Tarjetas de sonido": "sound-card",
    "Placas base": "motherboard",
    "Refrigeración y ventilación": "fan",
    "Memorias RAM": "RAM",
    #"componentes-pc-discos-ssd": "SSD",
    "Discos duros internos": "HDD",
    "Fuente alimentación PC": "power-source",
    "Cajas y torres": "tower",
    "componentes-pc-tarjetas-pci": "PCI"
}


class MediamarktSpider(CrawlSpider):
    name = 'mediamarkt-spider'
    allowed_domains = ['mediamarkt.es']
    start_urls = ['https://www.mediamarkt.es/es/category/componentes-56.html']

    rules = (
        Rule(LinkExtractor(allow=[
            #'cajas-y-torres',
            #'tarjetas-gr',
            'procesadores',
            #'placas-base',
            #'memorias-ram',
            #'discos-duros-internos',
            #'tarjetas-de-red',
            #'tarjetas-de-sonido',
            #'refrigeraci',
            #'fuente-alimentaci'
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
            component['height'] = dimensions[2]
            component['width'] = dimensions[1]

        elif 'potencia' in name.lower():
            component['power'] = value.lower().split('w')[0]

        elif 'interfa' in name.lower():
            component['socket'] = value

        elif 'storage' in name.lower() or 'capacidad' in name.lower():
            component['storing_capacity'] = value

        elif 'peso' in name.lower() or 'weig' in name.lower():
            component['weight'] = value

        elif 'frequ' in name.lower() or 'frecuen' in name.lower() or 'reloj' in name.lower():
            component['speed'] = value

        elif 'anchu' in name.lower():
            component['width'] = value

        elif 'altur' in name.lower():
            component['height'] = value

        elif 'socket' in name.lower():
            component['socket'] = value

        elif 'temp' in name.lower():
            component['max_temperature'] = value

        elif 'núcle' in name.lower():
            component['cores'] = value

        elif 'hilo' in name.lower():
            component['threads'] = value

        elif 'caché' in name.lower():
            component['storing_capacity'] = value

        elif 'tipo de memoria' in name.lower() or 'tipo de dispositivo' in name.lower():
            component['type'] = value



        return component

    def parse_component(self, response, component):
        component['source'] = 'mediamarkt'
        priceDiv = response.css("div.StyledBox-sc-1vld6r2-0.goTwsP")
        priceE = priceDiv.css("span:nth-child(2)::text").get()
        priceC = priceDiv.css("sup::text").get()
        print(priceE, priceC)

        #specsList

        yield component


    def parse_list(self, response):
        print('entrrooooooooooooooooooooooooooooooooooooooo')
        category = response.css("h1.eBQzgU::text").get()
        print('aaaaaaaaaaaaaaaaaaaaaaaa', category)
        components = response.css("div.StyledListItem-sc-7l2z3t-0.bilJsB")
        try:
            category = CATEGORIES[category]
            for component in components:
                name = components.css("p::text").get()
                link = component.css("a::attr(href)").get()
                link = 'https://www.mediamarkt.es' + link
                brand = match_brand(name)
                #print(brand)
                imagePrev = component.css("div.StyledBox-sc-1vld6r2-0.ekazDz.StyledFlexBox-sc-1w38xrp-2.fYnRFE")
                imageDiv = imagePrev.css("div.StyledFlexItem-sc-1vld6r2-1.fIQQcE.StyledFlexItem-sc-1w38xrp-3.StyledProductImageFlexItem-sc-1w38xrp-6.tjNrn.dcBEPE")
                imageDiv2 = imageDiv.css("div.StyledLazyImageWrapper-jly9io-0.iqZjnK")
                imageDiv3 = imageDiv2.css("div")
                imageDiv4 = imageDiv3.css("picture img::attr(src)").get()
                print('bbbbbbbbbbbbbbbbbbbbbb', imageDiv3)
                arg = {'component': Component(name=name, category=category, link=link, brand=brand)}
                yield response.follow(link, callback=self.parse_component, cb_kwargs=arg)
        except KeyError:
            print('entrooo')
            pass
        '''
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
        '''
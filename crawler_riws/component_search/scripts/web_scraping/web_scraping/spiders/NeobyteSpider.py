import scrapy, re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from crawler_riws.component_search.scripts.web_scraping.web_scraping.items import Component
from crawler_riws.component_search.scripts.web_scraping.web_scraping.spiders.utils.utils import match_brand


CARACT_TYPE = [
    {"name": "cores",
    "caract_values": ["núcleos", "núcleos:"]
    },
    {"name": "threads",
    "caract_values": ["hilos", "hilos:"]
    },
    {"name": "speed",
    "caract_values": ["frecuencia:", "frecuencia", "velocidad", "velolcidad"]
    },
    {"name": "storing_capacity",
    "caract_values": ["caché:", "caché", "memoria interna:", "capacidad:"]
    },
    {"name": "socket",
    "caract_values": ["socket"]
    },
    {"name": "power",
    "caract_values": ["tdp:"]
    },
    {"name": "latency",
    "caract_values": ["latencia:", "latencia"]
    },
    {"name": "type",
    "caract_values": ["tipo:", "tipo de memoria", "tipo de memoria:"]
    },
    {"name": "dimensiones",
    "caract_values": ["dimensiones:", "dimensiones"]
    },
    {"name": "weight",
    "caract_values": ["peso:"]
    },
]

COMPONENTES = {'placa base': "motherboard",
               'procesador': "processor",
               'memoria' : "RAM",
               'SSD' : "SSD",
               'HDD' : "HDD",
               'RAM' : "RAM",
               'gráfica': "graphic-card",
               'tarjeta de red': "net-card",
               'tarjeta de sonido': "sound-card",
               "ventilador": "fan",
               "fuente de alimentacion": "power-source",
               "caja": "tower"
            }

DESCARTES = ["voltaje de memoria:", "velocidad del bus:"]

class GigabyteSpider(CrawlSpider):
    name = 'neobyte-spider'
    allowed_domains = ['neobyte.es']
    start_urls = ['https://www.neobyte.es/']

    rules = (
        Rule(LinkExtractor(allow=[
            'procesadores-107',
            'placas-base-106',
            'memorias-ram-108',
            'ventilacion-109',
            'discos-duros-110',
            'tarjetas-graficas-111',
            'cajas-de-ordenador-112',
            'fuentes-de-alimentacion-113',
            'tarjetas-de-sonido-115',
            'conectividad-117',
        ]), callback='parse_list'),
    )

    def matchKey(self, key):
        for type in CARACT_TYPE:
            for value in type["caract_values"]:
                if value in key:
                    return type["name"]
    
    def descart(self, input):
        for d in DESCARTES:
            if d in input:
                return True

    def parse_socket(self, input, component):
        if input.find(':') == -1:
            component['socket'] = ''.join(input.split(' ')[1:])
        else:
            component['socket'] = ''.join(input.split(':')[1:])
    
    def parse_speed(self, input, component):
        data = ''.join(input.split(":")[1:]).replace(",", ".")
        if "hasta" in input:
            component['speed'] = float(re.sub('[áéíóúa-z:()]', '', ''.join(data.split("hasta")[1:])))           
        else:
            component['speed'] = float(re.sub('[áéíóúa-z:()]', '', data))
        
    def parse_component(self, response, component):
        component['brand'] = match_brand(component['name'])
        component['price'] = float(response.css("span.product-price::attr(content)").get())
        component['source'] = 'Neobyte'
        
        for caract in response.css('div.product-description li'):
            caract_text = caract.css("li::text").get().lower()
            name = self.matchKey(caract_text)
            
            if name == None or self.descart(caract_text): continue
 
            if name == "socket":
                self.parse_socket(caract_text, component)
                continue
                
            if name == "dimensiones":
                dimensiones_parsed = ''.join(caract_text.split(":")[1])
                component['height'] = dimensiones_parsed.split('x')[0]
                component['width'] = dimensiones_parsed.split('x')[1]
                continue
            
            if name == "type":
                component[name] = re.sub('[áéíóúa-z:()]', '', ''.join(caract_text.split(":")[1:]))
                continue
            
            if name == "speed":
                self.parse_speed(caract_text, component)
                continue
            
            if name == "latency" or name == "storing_capacity" or name == "weight":
                component[name] = float(re.sub('[áéíóúa-z:()]', '', ''.join(caract_text.split(":")[1:]).replace(",", ".")))
                continue
            
            component[name] = re.sub('[áéíóúa-z:()]', '', caract_text).replace(" ", "")
        
        yield component
        

    def parse_list(self, response):
        
        components = response.css("div.js-product-miniature-wrapper")
        for component in components:
            category = None
            name = component.css("span.h3.product-title a::text").get()   
             
            for n in name.lower().split():
                try:
                    category = COMPONENTES[n]
                    break 
                except KeyError:
                    continue
                
            if category == None: continue
            
            link = component.css("span.h3.product-title a::attr(href)").get()
            img = component.css("div.thumbnail-container img::attr(data-src)").get()
            
            arg = {'component': Component(name=name, link=link, image=img, category=category)}
            yield response.follow(link, callback=self.parse_component, cb_kwargs=arg)
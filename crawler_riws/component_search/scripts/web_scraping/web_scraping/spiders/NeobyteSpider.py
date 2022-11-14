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
    {"name": "speed",#para graficas que valor
    "caract_values": ["frecuencia:", "frecuencia", "velocidad", "velolcidad", "memory clock:"]
    },
    {"name": "socket",
    "caract_values": ["socket", "chip", "chips"]
    },
    {"name": "power",
    "caract_values": ["tdp:", "potencia", "total output"]
    },
    {"name": "latency",
    "caract_values": ["latencia:", "latencia"]
    },
    {"name": "type",
    "caract_values": ["tipo:", "tipo de memoria", "\ntipo de memoria", "tipo de memoria:", "memoria de vídeo:", "factor de forma",
                      "estándar de red"]
    },
    {"name": "storing_capacity",
    "caract_values": ["caché:", "caché", "capacidad", "capacidad:", "memoria de video:", "memoria interna:", "tamaño máximo de memoria:",
                      "canales de memoria"]
    },
    {"name": "dimensiones",
    "caract_values": ["dimensiones:", "dimensiones"]
    },
    {"name": "weight",
    "caract_values": ["peso:"]
    },
    {"name": "latency",
    "caract_values": ["latencia"]
    },
    {"name": "generation",
    "caract_values": ["generacion", "generation"]
    },
    {"name": "architecture",
    "caract_values": ["arquitectura"]
    },
    {"name": "max_temperature",
    "caract_values": ["arquitectura"]
    },
    {"name": "interface",
    "caract_values": ["interfaz" ,"interfaz:"]
    },
]

COMPONENTES = {'placa': "motherboard",
               'procesador': "processor",
               'memoria' : "RAM",
               'ssd' : "SSD",
               'hdd' : "HDD",
               'duro': "HDD",
               'ram' : "RAM",
               'gráfica': "graphic-card",
               'wifi': "net-card",
               'wifi': "net-card",
               'sonido': "sound-card",
               "ventilador": "fan",
               "fuente": "power-source",
               "caja": "tower"
            }

DESCARTES = ["voltaje de memoria:", "velocidad del bus:", "núcleos cuda:", "arquitectura de memoria",
             "dimensiones de tarjeta:", "núcleos cuda®:", "velocidad de datos max", "admite interfaz",
             "velocidad de rotación", "potencia de salida:", "velocidad de transferencia", "potencia de salida",
             "potencia de transmision", "potencia de transmisión"]

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
            'discos-duros-3-5-sata-142',
            'discos-duros-ssd-144',
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
            if "chip" in input or "para procesadores" in input or "processors" in input:
                component['socket'] = input
            else:
                component['socket'] = ''.join(input.split(' ')[1:])
        else:
            component['socket'] = ''.join(input.split(':')[1:])
    
    def parse_speed(self, input, component):
        data = ''.join(input.split(":")[1:]).replace(",", ".")
        if "hasta" in input:
            component['speed'] = float(re.sub('[áéíóúa-z:()]', '', ''.join(data.split("hasta")[1:])))           
        else:
            component['speed'] = float(re.sub('[áéíóúa-z:()]', '', data))
        
    def parse_opinions(self, input, component):
        if "/" in input:
            component['rating'] = float(input[input.find("(")+1:input.find("/")])
        else:
            component['rating'] = None
            
    def parse_generation(self, input, component):
        if input.find(".ª"):
            component['generation'] = int(input[input.find("ª")-3:input.find("ª")-1])
        elif re.search('[0-9]th', input):
            component['generation'] = int(input[input.find("th ")-3:input.find("th ")-1])
        
    def parse_component(self, response, component):
        component['brand'] = match_brand(component['name'])
        component['price'] = float(response.css("span.product-price::attr(content)").get())
        component['source'] = 'Neobyte'
        self.parse_opinions(response.css("span.iqitreviews-title::text").get(), component)
        
        for caract in response.css('div.product-description li'):
            try: 
                caract_text = caract.css("li::text").get().lower()
                name = self.matchKey(caract_text)
                
                if name == None or self.descart(caract_text) or component[name] != None: continue
    
                if name == "socket":
                    self.parse_socket(caract_text, component)
                    continue
                    
                if name == "dimensiones":
                    dimensiones_parsed = ''.join(caract_text.split(":")[1])
                    component['height'] = dimensiones_parsed.split('x')[0]
                    component['width'] = dimensiones_parsed.split('x')[1]
                    continue
                
                if name == "speed":
                    self.parse_speed(caract_text, component)
                    continue
                
                if name in ["architecture", "generation", "year", "interface", "type"]: #latencia
                    component[name] = ''.join(caract_text.split(":")[1:])
                    continue
                
                if name in ["latency", "storing_capacity", "weight"]:
                    component[name] = float(re.sub('[áéíóúa-z:()]', '', ''.join(caract_text.split(":")[1:]).replace(",", ".")))
                    if name == "storing_capacity" and "tb" in caract_text:
                        component[name] = component[name] * 1000
                    continue
                
                component[name] = re.sub('[áéíóúa-z:()]', '', caract_text).replace(" ", "")
            except Exception:
                continue
        
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
                
            if "caja externa" in name.lower(): continue
            if category == None: continue
            
            link = component.css("span.h3.product-title a::attr(href)").get()
            img = component.css("div.thumbnail-container img::attr(data-src)").get()
            
            arg = {'component': Component(name=name, link=link, image=img, category=category)}
            yield response.follow(link, callback=self.parse_component, cb_kwargs=arg)
import scrapy, re
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from crawler_riws.component_search.scripts.web_scraping.web_scraping.items import Component
from crawler_riws.component_search.scripts.web_scraping.web_scraping.spiders.utils.utils import match_brand


COMPONENTES = {'placa': "motherboard",
               'procesador': "processor",
               'memoria' : "RAM",
               'ssd' : "SSD",
               'hdd' : "HDD",
               'duro': "HDD",
               'ram' : "RAM",
               'gráfica': "graphic-card",
               'wifi': "net-card",
               'sonido': "sound-card",
               "ventilador": "fan",
               "fuente": "power-source",
               "caja": "tower"
            }

CARACT_TYPE = [
    {"name": "cores",
    "caract_values": ["núcleos"]
    },
    {"name": "threads",
    "caract_values": ["hilos"]
    },
    {"name": "speed",
    "caract_values": ["frecuencia base", "velocidad", "velocidad de memoria"]
    },
    {"name": "socket",
    "caract_values": ["socket", "chip", "chips", "sockets"]
    },
    {"name": "power",
    "caract_values": ["tdp:", "potencia", "total output", "fuente de alimentación"]
    },
    {"name": "latency",
    "caract_values": [ "latencia"]
    },
    {"name": "type",
    "caract_values": ["tipos de memoria", "tipo de memoria", "factor de forma",
                      "estándar de red", "factor de forma"]
    },
    {"name": "storing_capacity",
    "caract_values": ["caché del procesador", "capacidad", "memoria de video", "memoria interna", "tamaño máximo de memoria"]
    },
    {"name": "weight",
    "caract_values": ["peso"]
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
    {"name": "interface",
    "caract_values": ["interfaz"]
    },
    {"name": "width",
    "caract_values": ["ancho"]
    },
    {"name": "height",
    "caract_values": ["altura"]
    },
    {"name": "weight",
    "caract_values": ["peso"]
    },
]

DESCARTES = ["compatible con modulación", "velocidades de reloj", "ancho de banda de memoria", "conector de potencia"]

class PcBoxSpider(CrawlSpider):
    name = 'pcbox-spider'
    allowed_domains = ['pcbox.com']
    start_urls = ['https://www.pcbox.com/']

    rules = (
        Rule(LinkExtractor(allow=[
            'componentes-de-ordenador',
            #'componentes-de-ordenador/procesadores',
            #'componentes-de-ordenador/discos-duros',
            'componentes-de-ordenador/cajas-de-pc',
            #'componentes-de-ordenador/fuentes-de-alimentacion',
            #'componentes-de-ordenador/memoria-ram',
            #'componentes-de-ordenador/placas-base',
            #'componentes-de-ordenador/ventiladores-ordenador',
            'componentes-de-ordenador/tarjetas-graficas',
            'componentes-de-ordenador/tarjetas-de-sonido'
        ]), callback='parse_list', follow=True),
    )
    
    def matchKey(self, key):
        for type in CARACT_TYPE:
            for value in type["caract_values"]:
                if value in key:
                    return type["name"]
    
    def descartar(self, input):
        for d in DESCARTES:
            if d in input:
                return True
    
    def parse_component(self, response, component):
        component['brand'] = match_brand(component['name'])
        Peuros = response.css("span.vtex-product-price-1-x-currencyInteger ::text").get()
        Pcent = response.css("span.vtex-product-price-1-x-currencyFraction ::text").get()
        component['price'] = float(Peuros + "." + Pcent)
        component['source'] = 'PcBox'
   
        for caract in response.css('tr.vtex-table-description-row'):
            try:
                key = caract.css("b::text").get()
                value = caract.css("td.vtex-table-description-value::text").get()
                
                if key == None or value == None: continue
                name = self.matchKey(key.lower())
                
                if name == None or self.descartar(key.lower()) or component[name] != None: continue
                
                if name in ["latency", "storing_capacity", "weight", "speed", "power", "width", "height"]:
                        component[name] = float(re.sub('[/áéíóúa-z:()-]', '', value.lower().replace(",", ".")))
                        continue
                
                component[name] = value
            except KeyError or Exception or ValueError:
                component[name] = None
        yield component

    def parse_list(self, response):
        components = response.css("div.vtex-search-result-3-x-galleryItem")
        for component in components:
            category = None
            name = component.css("span.vtex-product-summary-2-x-brandName ::text").get()
            
            for n in name.lower().split():
                try:
                    category = COMPONENTES[n]
                    break 
                except KeyError:
                    continue
                
            if category == None: continue
            if "ssd" in name.lower(): category = "SSD"
            
            link = self.start_urls[0] + component.css("section.vtex-product-summary-2-x-containerNormal--main-product-summary a::attr(href)").get()
            img = component.css("div.vtex-product-summary-2-x-imageStackContainer img::attr(src)").get()
            
            arg = {'component': Component(name=name, link=link, image=img, category=category)}
            yield response.follow(link, callback=self.parse_component, cb_kwargs=arg)
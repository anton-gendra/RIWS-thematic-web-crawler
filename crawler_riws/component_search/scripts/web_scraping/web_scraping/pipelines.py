# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .items import Component
from crawler_riws.component_search.elastic.ESController import ESController,idx
from scrapy.exceptions import DropItem
from crawler_riws.crawler_riws.settings import INDICES

class WebScrapingPipeline(object):
    
    def __init__(self):
        self.index = ESController()
        self.index.create_index(INDICES['component'], idx)
    
    def process_item(self, item, spider):    
        # if not isinstance(item, Component):
        #     raise DropItem(f"Incorrect element{item}")
        
        if not item['category'] or not item['source'] or not item['brand']:
            raise DropItem(f"Incorrect data item {item}")
        
        self.index.insert_component(self.indexName, self.componentToElasticItem(item))
        print(f"Item añadido, id: {item['name']}")
        return item
        
    def open_spider(self, spider):
        self.indexName = INDICES['component']
    
    def componentToElasticItem(self, item):
        return{
            "name": item["name"],
            "price": item["price"],
            "brand": item["brand"],
            "source": item["source"],
            "link": item["link"],
            "category": item["category"],
            "characteristics": {
                "storing_capacity": item["storing_capacity"],
                "height": item["height"],
                "width": item["width"],
                "weight": item["weight"],
                "power": item["power"],
                "speed": item["speed"],
                "latency": item["latency"],
                "max_temperature": item["max_temperature"],
                "year": item["year"],
                "generation": item["generation"],
                "rating": item["rating"],
                "socket": item["socket"],
                "interface": item["interface"],
                "achitecture": item["achitecture"],
                "cores": item["cores"],
                "threads": item["threads"],
                "type": item["type"]
            }
        }
        
    #def close_spider(self, spider):
        #cerrar indice de elastic
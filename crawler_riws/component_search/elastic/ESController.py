from typing import Any, Dict, Tuple
from elasticsearch import Elasticsearch, BadRequestError
import requests
import os, sys

from crawler_riws.settings import INDICES # Here we can access indices names


idx = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "id": {
                "type": "keyword"
            },
            "name": {
                "type": "text"
            },
            "price": {
                "type": "float"
            },
            "brand": {
                "type": "keyword"
            },
            "source": { # Page {Gigabyte, Fnac, whatever}
                "type": "keyword"
            },
            "link": {
                "type": "keyword",
                "index": False
            },
            "category": {
                "type": "keyword"
            },
            "image": {
                "type": "keyword",
                "index": False
            },
            "characteristics": {
                "type": "nested", 
                "properties": {
                    "type": "nested", 
                    "storing_capacity": { # Gigabytes, RAM or persistent or w/e
                        "type": "integer"
                    },
                    "height": {
                        "type": "float"
                    },
                    "width": {
                        "type": "float"
                    },
                    "weight": {
                        "type": "float"
                    },
                    "power": { # Watts of power
                        "type": "integer"
                    },
                    "speed": {
                        "type": "float"
                    },
                    "latency": {
                        "type": "integer"
                    },
                    "max_temperature": {
                        "type": "integer"
                    },
                    "year": {
                        "type": "integer"
                    },
                    "generation": {
                        "type": "integer"
                    },
                    "rating": {
                        "type": "integer"
                    },
                    "socket": {
                        "type": "keyword"
                    },
                    "interface": {
                        "type": "keyword"
                    },
                    "architecture": {
                        "type": "keyword"
                    },
                    "cores": {
                        "type": "keyword"
                    },
                    "threads": {
                        "type": "keyword"
                    },
                    "type": {
                        "type": "keyword"
                    }
                }
            }
        }
    }
}


class ESController:
    base_url = "http://elastic:" + os.environ['ES_PASSWORD'] + "@localhost:9200/"
    es = Elasticsearch(base_url)

    def get_es_status(self) -> Tuple[Tuple[int, str], str]:
        result = requests.get(self.base_url)
        return (result.status_code, result.reason), result.content.decode('utf-8')


    # To remove an index we can do: curl -X DELETE http://elastic:<password>@localhost:9200/<index_name>
    def create_index(self, index_name: str, mapping: Dict[str, Any]):
        try:
            result = self.es.indices.create(index=index_name, body=mapping)
        
        except BadRequestError as e:
            return e.meta.status, e.error

        return result.body

    def get_index_status(self, index_name: str) -> Tuple[Tuple[int, str], str]:
        result = requests.get(self.base_url + index_name)
        return (result.status_code, result.reason), result.content.decode('utf-8')

    def get_component_by_name(self, name: str):
        query = {
            "match": {
                "name": name
            }
        }
        source = ["id", "name", "price", "brand", "characteristics", "image"]
        result = self.es.search(query=query, size=10, index=INDICES['component'], 
            _source=source)
        return [component['_source'] for component in result['hits']['hits']]

    def insert_component(self, index_name: str, data: Dict[str, Any]):
        data['id'] = f"{data['name']}-{data['source']}"
        query = {
            "match": {
                "id": data['id']
            }
        }
        exact_match = self.es.search(query=query, size=1, index=INDICES['component'], _source=['id'])
        if exact_match['hits']['hits']: return {'status': 400, 'description': "Component already inserted"}

        result = self.es.index(index=index_name, document=data)
        return result

    def get_component_by_price(self, data: Dict[str, Any]):
        
        query = {
                "bool": {
                    "filter": [
                        { "term": {"category": data['category']}}
                    ],
                    "must": [
                        { "bool": {
                                "should": [
                                { "term": {"brand": "Kingstone"}},
                                { "term": {"brand": "Gigabyte"}}]
                            }
                        },
                        {"range": {
                                "price" : {"gte": data['min'], "lte": data['max']}
                            }
                        },
                        {
                        "nested": {
                            "path": "characteristics",
                            "query": {
                                "bool": {
                                    "must": [
                                        { "match": { "characteristics.socket": "LG234" } },
                                        { "match": { "characteristics.storing_capacity": 5000 } }
                                    ]
                                } 
                            }
                        }
                        }
                    ],
                }
            }
        source = ["id", "name", "price", "brand", "source", "link", "image", "characteristics"]
        result = self.es.search(query=query, size=20, index=INDICES['component'], _source=source)
        return result

    def create_query_and(self, andQ):
        listAnd = []
        for q in andQ:
            listAnd.append(
                { "match": { "characteristics." + q['key']: q['value'] } }
            )
            
        caract = {"nested": {
                    "path": "characteristics",
                    "query": {
                        "bool": {
                            "must": listAnd
                        } 
                    }
                }
            }
        return caract

    def create_query_or(self, orQ):
        listOr = []
        for q in orQ:
            values= []
            for value in q['values']:
                values.append({ "term": { q['key']: value } })
                
            listOr.append({
                "bool": {
                    "should": values
                }
            })
            
        return listOr 
    
    def create_query_price(self, priceQ):
        if priceQ['min'] == None:
            priceQ['min'] = 0
            
        if priceQ['max'] == None:
            priceQ['max'] == sys.float_info.max
        
        return  {"range": {"price" : {"gte": priceQ['min'], "lte": priceQ['max']}}}
    
    def search(self, data):
        args = []
        list(map(lambda q: args.append(q), self.create_query_or(data['orQ']))) 
        args.append(self.create_query_price(data["price"]))
        args.append(self.create_query_and(data['andQ']))
        
        query = {
            "bool": {
                "must": args
            }
        }
        if data['category'] != None:
            query["bool"]["filter"] = { "term": {"category": data['category']}}
            
        if data['name'] != None:
            query["bool"]["must"].append(
                {"match" : { "name" : data['name'] }}
            )
            
        print(query)
        print("\n")
        source = ["id", "name", "price", "brand", "source", "category", "characteristics"]
        result = self.es.search(query=query, size=20, index=INDICES['component'], _source=True)
        
        return result['hits']['hits']
    
    

if __name__ == '__main__':
    elastic = ESController()
    #print(f"Elasticsearch server status: {elastic.get_es_status()}")
    # print(elastic.create_index("test_index", idx))
    # print(elastic.get_index_status("test_index"))
    #print(f"Creating new index '{INDICES['component']}': {elastic.create_index(INDICES['component'], idx)}")
    #print(f"Index status: {elastic.get_index_status(INDICES['component'])}")
    component_1 = {
        "name": "Cisco SSD 2349k",
        "price": 30.14,
        "brand": "Kingstone",
        "source": "CoolMod",
        "category": "almacenamiento",
        "image": "AA",
        "link": "AA",
        "characteristics": {
            "socket": "LG234",
            "storing_capacity": 5000,
            "year": 2022
        }
    }
    component_2 = {
        "name": "Nicolas Motherboard 2349k",
        "price": 89.67,
        "brand": "Gigabyte",
        "source": "Gigabyte",
        "category": "almacenamiento",
        "image": "AA",
        "link": "AA",
        "characteristics": {
            "socket": "LG234",
            "year": 2022
        }
    }
    component_3 = {
        "name": "Arthur Processor",
        "price": 139.43,
        "brand": "Asus",
        "source": "Gigabyte2",
        "category": "almacenamiento",
        "image": "AA",
        "link": "AA",
        "characteristics": {
            "socket": "LG234",
            "speed": 1000,
            "year": 2022
        }
    }
    
    component_4 = {
        "name": "BBBBB 2323",
        "price": 110.67,
        "brand": "Gigabyte",
        "source": "Gigabyte",
        "category": "almacenamiento",
        "characteristics": {
            "socket": "LG234",
            "year": 2022
        }
    }
    
    args = {
        "name": "PROCESADOR AMD RYZEN 5 5600G 3.9GHZ SKT AM4 65W",
        "category" : "processor",
        "price": {
            "min": 5,
            "max": 2000
        }, 
        "orQ": [],
        "andQ": []
    }
    
    {"key": "brand", "values": ["AMD", "INTEL", "Asus"]}, {"key": "source", "values": ["PcBox", "Gigabyte", "Gigabyte2"]}
    {"key": "socket", "value": "LG234"}, {"key": "year", "value": 2022}
    
    #print(f"Inserting component 1: {elastic.insert_component(INDICES['component'], component_1)}")
    #print(f"Inserting component 2: {elastic.insert_component(INDICES['component'], component_2)}")
    #print(f"Inserting component 3: {elastic.insert_component(INDICES['component'], component_3)}")
    #print(f"Inserting component 4: {elastic.insert_component(INDICES['component'], component_4)}")

    print(f"Searching general query: {elastic.search(args)}")
    
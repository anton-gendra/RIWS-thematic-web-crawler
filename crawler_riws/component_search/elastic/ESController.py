from typing import Any, Dict, Tuple
from elasticsearch import Elasticsearch, BadRequestError
import requests
import os

from crawler_riws.crawler_riws.settings import INDICES # Here we can access indices names

# TODO: Remove
# Hago este sólo de ejemplo, luego vemos cómo hacemos
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
                "url": "keyword",
                "index": False
            },
            "characteristics": {
                "properties": {
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
                        "type": "integer"
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
                    "category": {
                        "type": "keyword"
                    },
                    "achitecture": {
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
        source = ["id", "name", "price", "brand", "characteristics"]
        result = self.es.search(query=query, size=10, index=INDICES['component'], 
            _source=source)
        return result

    def insert_component(self, index_name: str, data: Dict[str, Any]):
        data['id'] = f"{data['name']}-{data['source']}"
        query = {
            "match": {
                "id": data['id']
            }
        }
        exact_match = self.es.search(query=query, size=1, index=INDICES['component'], _source=['id'])
        xd = exact_match['hits']['hits']
        if exact_match['hits']['hits']: return {'status': 400, 'description': "Component already inserted"}

        result = self.es.index(index=index_name, document=data)
        return result


if __name__ == '__main__':
    elastic = ESController()
    print(f"Elasticsearch server status: {elastic.get_es_status()}")
    # print(elastic.create_index("test_index", idx))
    # print(elastic.get_index_status("test_index"))
    # print(f"Creating new index '{INDICES['component']}': {elastic.create_index(INDICES['component'], idx)}")
    print(f"Index status: {elastic.get_index_status(INDICES['component'])}")
    component_1 = {
        "name": "Cisco SSD 2349k",
        "price": 3.14,
        "brand": "Kingstone",
        "source": "Gigabyte",
        "characteristics": {
            "storing_capacity": 5000
        }
    }
    component_2 = {
        "name": "Nicolas Motherboard 2349k",
        "price": 89.67,
        "brand": "Gigabyte",
        "source": "Gigabyte",
        "characteristics": {
            "socket": "LG234"
        }
    }
    component_3 = {
        "name": "Arthur Processor 8300N",
        "price": 149.43,
        "brand": "Asus",
        "source": "Gigabyte",
        "characteristics": {
            "socket": "LG234",
            "speed": 1000
        }
    }
    print(f"Inserting component 1: {elastic.insert_component(INDICES['component'], component_1)}")
    print(f"Inserting component 2: {elastic.insert_component(INDICES['component'], component_2)}")
    print(f"Inserting component 3: {elastic.insert_component(INDICES['component'], component_3)}")
    print(f"Searching 'SSD' term: {elastic.get_component_by_name('SSD')}")
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
            "name": {
                "type": "text"
            },
            "price": {
                "type": "float"
            },
            "characteristics": {
                "properties": {
                    "storing_capacity": { # Gigabytes, RAM or persistent or w/e
                        "type": "integer"
                    },
                    "height": {
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



if __name__ == '__main__':
    elastic = ESController()
    print(elastic.get_es_status())
    print(elastic.create_index("test_index", idx))
    print(elastic.get_index_status("test_index"))
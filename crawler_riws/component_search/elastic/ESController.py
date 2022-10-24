import requests
import os


class ESController:

    def __init__(self):
        self.base_url = "http://elastic:" + os.environ['ES_PASSWORD'] + "@localhost:9200/"

    def get_status(self):
        return requests.get(self.base_url)


if __name__ == '__main__':
    elastic = ESController()
    print(elastic.get_status())
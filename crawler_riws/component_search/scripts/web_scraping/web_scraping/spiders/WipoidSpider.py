import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from web_scraping.items import Component


class WipoidSpider(CrawlSpider):
    name = 'wipoid-spider'
    allowed_domains = ['wipoid.com']
    start_urls = ['https://www.wipoid.com/']

    rules = (
        Rule(LinkExtractor(allow=[
            'procesadores',
            'placas-base',
            'ventiladores',
            'tarjetas-graficas',
            'memoria-ram',
            'refrigeracion-cpu',
            'discos-duros',
            'fuentes-alimentacion',
            'torres-cajas-carcasas',
            'grabadoras-dvd-blu-ray',
            'accesorios-caja',
            'cables-y-adaptadores'
        ]), callback='parse_list'),
    )

    def parse_component(self, response, component):
        #print('RESPONSEEEEEEEEE:',response)
        #print('COMPONENTTTTTTTT:',component)
        #print(response.css("section.page-product-box p::text").getall())
        #print('NAMEEEEEEE:', component["name"])
        productLabels = response.css("div.prd-reference a::text").getall()
        brand = productLabels[1] if (len(productLabels) == 2) else None
        print('BRAND:', brand)
        price = response.css("div.our_price_display span::text").get()
        print('priceeeeeeee:',price)
        specsList = response.css("section.page-product-box p::text").getall()
        link = response.url
        #print('sourceee:', link[8:].split('/')[0])
        source = 'wipoid'
        print('listaaaaa:', specsList)
        yield component

    def parse_list(self, response):
        category = response.css("h1.category-name::text").get().strip()
        components = response.css("div.item-inner")
        for component in components:
            name = component.css("a.product-name::text").get().strip()
            link = component.css("div.item-title a::attr(href)").get()
            image = component.css("img.replace-2x::attr(src)").get()

            arg = {'component': Component(name=name, category=category, link=link, image=image)}
            yield response.follow(link, callback=self.parse_component, cb_kwargs=arg)
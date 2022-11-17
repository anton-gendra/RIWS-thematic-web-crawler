from django.http import HttpResponse
from django.shortcuts import render
from .forms import FilterForm
from component_search.elastic.ESController import ESController
from crawler_riws.settings import COMPONENT_CAREGORIES
from component_search.scripts.web_scraping.web_scraping.spiders.utils.utils import BRANDS
from django.core.exceptions import ObjectDoesNotExist
from component_search.scripts.web_scraping.web_scraping.items import Component

from django.views.decorators.csrf import csrf_exempt

import json

from component_search.models import Click

def search(request):
    context = {"components_categories": COMPONENT_CAREGORIES}

    return render(request, 'index.html', context)

def filter(request):
    es = ESController()

    name = None
    category = None
    min_price = None
    max_price = None
    brand = None

    if request.GET:
        name = request.GET.get('name')
        category = request.GET.get('category')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        brand = request.GET.get('brand')

    args = {
        "name": name,
        "category" : category,
        "price": {
            "min": min_price,
            "max": max_price
        }, 
        "orQ": [{"key": "brand", "values": [brand]}],
        "andQ": []
    }

    elastic_search_data = es.search(args)
    components = []

    for data in elastic_search_data:
        components.append(Component(name=data._source.name, price=data._source.price, brand=data._source.brand, source=data._source.source, link=data._source.link, category=data._source.category, image=data._source.image, storing_capacity=data._source.characteristics.storing_capacity, height=data._source.characteristics.height, width=data._source.characteristics.width, wheight=data._source.characteristics.wheight, power=data._source.characteristics.power, speed=data._source.characteristics.speed, latency=data._source.characteristics.latency, max_temperature=data._source.characteristics.max_temperature, year=data._source.characteristics.year, generation=data._source.characteristics.generation, rating=data._source.characteristics.rating, socket=data._source.characteristics.socket, interface=data._source.characteristics.interface, architecture=data._source.characteristics.architecture, cores=data._source.characteristics.cores, threads=data._source.characteristics.threads, type=data._source.characteristics.type))

    for component in components:
        try:
            clicks = Click.objects.get(component=component['id']).clicks

        except ObjectDoesNotExist:
            clicks = 0

        component['clicks'] = clicks

    components.sort(key=lambda component: component['clicks'], reverse=True)

    context = {
        'components_categories': COMPONENT_CAREGORIES,
        'brands': BRANDS,
        'name': name,
        'category': category,
        'min_price': min_price,
        'max_price': max_price,
        'brand': brand,
        'components': components
    }

    print(context)
    return render(request, 'filter.html', context)

@csrf_exempt
def update_component_clicks(request):
    component_id = request.body.decode('utf-8')

    if not component_id:
        return HttpResponse({'detail': 'Component id not supplied'}, content_type='application/json')

    try:
        click_obj = Click.objects.get(component=component_id)
    
    except ObjectDoesNotExist:
        click_obj = Click.objects.create(component=component_id)

    click_obj.clicks += 1
    click_obj.save()

    return HttpResponse({'detail': 'Click saved'}, content_type='text/json')
from django.http import HttpResponse
from django.shortcuts import render
from .forms import FilterForm
from component_search.elastic.ESController import ESController
from crawler_riws.settings import COMPONENT_CAREGORIES, COMPONENT_SOURCES
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
    socket  = None
    storing_capacity = None
    power = None
    max_temperature = None
    speed = None
    weight = None
    height = None
    width = None

    if request.GET:
        name = request.GET.get('name')
        name = name if name else None
        category = request.GET.get('category')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        orq = []
        brand = request.GET.getlist('brand')
        if brand and brand[0]:
            orq.append({"key": "brand", "values": brand})
        source = request.GET.getlist('source')
        if source and source[0]:
            orq.append({"key": "source", "values": source})
        andq = []
        socket  = request.GET.get('socket')
        if socket:
            andq.append({"key": "socket", "value": socket})
        storing_capacity = request.GET.get('storing_capacity')
        if storing_capacity:
            andq.append({"key": "storing_capacity", "value": storing_capacity})
        power = request.GET.get('power')
        if power:
            andq.append({"key": "power", "value": power})
        max_temperature = request.GET.get('max_temperature')
        if max_temperature:
            andq.append({"key": "max_temperature", "value": max_temperature})
        speed = request.GET.get('speed')
        if speed:
            andq.append({"key": "speed", "value": speed})
        weight = request.GET.get('weight')
        if weight:
            andq.append({"key": "weight", "value": weight})
        height = request.GET.get('height')
        if height:
            andq.append({"key": "height", "value": height})
        width = request.GET.get('width')
        if width:
            andq.append({"key": "width", "value": width})

        args = {
                "name": name,
                "category" : category,
                "price": {
                    "min": min_price,
                    "max": max_price
                }, 
                "orQ": orq,
                "andQ": andq
            }
        elastic_search_data = es.search(args)

    components = []

    for data in elastic_search_data:
        data_source = data['_source']
        data_source_characteristics = data['_source']['characteristics']
        components.append(Component(
            id=data_source['id'],
            name=data_source['name'], 
            price=data_source['price'], 
            brand=data_source['brand'], 
            source=data_source['source'], 
            link=data_source['link'], 
            category=data_source['category'], 
            image=data_source['image'], 
            storing_capacity=data_source_characteristics['storing_capacity'], 
            height=data_source_characteristics['height'], 
            width=data_source_characteristics['width'], 
            weight=data_source_characteristics['weight'], 
            power=data_source_characteristics['power'], 
            speed=data_source_characteristics['speed'], 
            latency=data_source_characteristics['latency'], 
            max_temperature=data_source_characteristics['max_temperature'], 
            year=data_source_characteristics['year'], 
            generation=data_source_characteristics['generation'], 
            rating=data_source_characteristics['rating'], 
            socket=data_source_characteristics['socket'], 
            interface=data_source_characteristics['interface'], 
            architecture=data_source_characteristics['architecture'], 
            cores=data_source_characteristics['cores'], 
            threads=data_source_characteristics['threads'], 
            type=data_source_characteristics['type']
        ))

    for component in components:
        try:
            clicks = Click.objects.get(component=component['id']).clicks

        except ObjectDoesNotExist:
            clicks = 0

        component['clicks'] = clicks

    components.sort(key=lambda component: component['clicks'], reverse=True)

    context = {
        'components_categories': COMPONENT_CAREGORIES,
        'component_sources': COMPONENT_SOURCES,
        'brands': BRANDS,
        'name': name,
        'category': category,
        'min_price': min_price,
        'max_price': max_price,
        'brand': brand,
        'socket': socket,
        'storing_capacity': storing_capacity,
        'power': power,
        'max_temperature': max_temperature,
        'speed': speed,
        'weight': weight,
        'height': height,
        'width': width,
        'source': source,
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
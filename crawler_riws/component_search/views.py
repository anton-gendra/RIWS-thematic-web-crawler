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
        brand = request.GET.getlist('brand')

        args = {
                "name": name,
                "category" : category,
                "price": {
                    "min": min_price,
                    "max": max_price
                }, 
                "orQ": [],
                "andQ": []
            }
        elastic_search_data = es.search(args)

    components = []

    for data in elastic_search_data:
        data_source = data['_source']
        data_source_characteristics = data['_source']['characteristics']
        components.append(Component(
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
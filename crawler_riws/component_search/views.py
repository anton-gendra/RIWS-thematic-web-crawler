from django.shortcuts import render
from .forms import FilterForm
from component_search.elastic.ESController import ESController
from crawler_riws.settings import COMPONENT_CAREGORIES
from component_search.scripts.web_scraping.web_scraping.spiders.utils.utils import BRANDS

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

    components = es.get_component_by_name(name if name else '')

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
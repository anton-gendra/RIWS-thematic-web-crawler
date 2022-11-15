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

    if request.GET:
        name = request.GET.get('name')
        category = request.GET.get('category')

    components = es.get_component_by_name('SSD') # SSD es solo de prueba borra esto
    form = FilterForm()
    context = {
        'components_categories': COMPONENT_CAREGORIES,
        'brands': BRANDS,
        'params': name,
        'components': components
    }

    print(context)
    return render(request, 'filter.html', context)
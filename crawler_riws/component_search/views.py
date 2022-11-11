from django.shortcuts import render
from .forms import FilterForm
from component_search.elastic.ESController import ESController

def search(request):
    components_categories = ['Graphics-Card', 'Laptop', 'Monitor', 'Desktops', 'PC-Peripherals', 'Keyboard', 'Mouse', 'Headset', 'PC-Components', 'PC-Case', 'Power-Supply', 'CPU-Cooler', 'SSD', 'Memory', 'DIY-KIT']
    context = {"components_categories": components_categories}

    return render(request, 'index.html', context)

def filter(request):
    es = ESController()

    if request.GET:
        search_key = request.GET.get('search_input')

    components = es.get_component_by_name('SSD') # SSD es solo de prueba borra esto
    form = FilterForm()
    context = {
        'form': form,
        'result': search_key,
        'components': components
    }

    print(context)
    return render(request, 'filter.html', context)
from django.shortcuts import render
from .forms import FilterForm

def search(request):
    components_categories = ['Graphics-Card', 'Laptop', 'Monitor', 'Desktops', 'PC-Peripherals', 'Keyboard', 'Mouse', 'Headset', 'PC-Components', 'PC-Case', 'Power-Supply', 'CPU-Cooler', 'SSD', 'Memory', 'DIY-KIT']
    context = {"components_categories": components_categories}

    return render(request, 'index.html', context)

def filter(request):
    if request.GET:
        form = FilterForm()
        context = {
            'form': form,
            'result': request.GET.get('search_input')
        }
    print(context)
    return render(request, 'filter.html', context)
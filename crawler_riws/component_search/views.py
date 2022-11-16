from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

from django.views.decorators.csrf import csrf_exempt

import json

from component_search.models import Click

def search(request):
    context = None
    if request.GET:
        context = {
            'result': request.GET['search-input']
        }

    return render(request, 'index.html', context)

@csrf_exempt
def update_component_clicks(request):
    component_id = json.loads(request.body.decode('utf-8')).get('component_id')

    if not component_id:
        return HttpResponse({'detail': 'Component id not supplied'}, content_type='application/json')

    try:
        click_obj = Click.objects.get(component=component_id)
    
    except ObjectDoesNotExist:
        click_obj = Click.objects.create(component=component_id)

    click_obj.clicks += 1
    click_obj.save()

    return HttpResponse({'detail': 'Click saved'}, content_type='text/json')
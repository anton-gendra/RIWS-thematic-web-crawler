from django.shortcuts import render

def search(request):
    context = None
    if request.GET:
        context = {
            'result': request.GET['search-input']
        }

    return render(request, 'index.html', context)
from django.urls import path
from component_search import views

urls = [
    path('', views.search, name='main_page'),
    path('index.html', views.search, name='main_page'),

    path('update-click', views.update_component_clicks, name='update_click'),
    path('filter.html', views.filter, name='filter_page'),
]
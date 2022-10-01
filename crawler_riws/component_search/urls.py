from django.urls import path
from component_search import views

urls = [
    path('', views.search, name='main_page')
]
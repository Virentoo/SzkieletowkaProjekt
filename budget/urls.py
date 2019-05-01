from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('base', views.base, name='base'),
    path('base/recent', views.base_recent, name='base/recent'),
    path('base/new', views.home, name='base/new'),
]

from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('base', views.home, name='home'),
]

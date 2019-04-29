from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('base', views.base, name='base'),
    path('base/newincome', views.home, name='base/newincome'),
    path('base/newexpense', views.home, name='base/newexpense'),
]

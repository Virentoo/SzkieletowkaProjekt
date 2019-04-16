from django.urls import path

from . import views

urlpatterns = [
	# ex: /budget/
    path('', views.home, name='home'),
]
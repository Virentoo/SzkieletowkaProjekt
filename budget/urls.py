from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('budget', views.budget, name='budget'),
    path('budget/recent', views.budget_recent, name='budget/recent'),
    path('budget/new', views.home, name='budget/new'),
    path('budget/get_budget/', views.get_budget, name='get_budget'),
]

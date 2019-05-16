from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('budget', views.budget, name='budget'),
    path('budget/recent', views.budget_recent, name='budget/recent'),
    path('budget/new_expense', views.new_expense, name='budget/new_expense'),
    path('budget/new_income', views.new_income, name='budget/new_income'),
    #path('budget/chart', views.chart, name='budget/chart'),
    path('budget/get_budget/', views.get_budget, name='get_budget'),
]

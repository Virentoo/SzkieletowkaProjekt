from django.urls import path
from .views import NewTransactionView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('budget', views.budget, name='budget'),
    path('budget/recent', views.budget_recent, name='budget/recent'),
    path('budget/new', NewTransactionView.as_view(), name='budget/new'),
    #path('budget/chart', views.chart, name='budget/chart'),
    path('budget/get_budget/', views.get_budget, name='get_budget'),
]

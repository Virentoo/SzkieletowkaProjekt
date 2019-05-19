from django.urls import path
from .views import NewTransactionView,NewCategoryView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('budget', views.budget, name='budget'),
    path('budget/recent', views.budget_recent, name='budget/recent'),
    path('budget/new', NewTransactionView.as_view(), name='budget/new'),
    path('budget/new_category', NewCategoryView.as_view(), name='budget/new_category'),
    path('budget/chart', views.chart, name='budget/chart'),
    path('budget/get_budget/', views.get_budget, name='get_budget'),
    path('budget/delete', views.delete, name='budget_delete'),

]

from django.urls import path
from .views import NewCategoryView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('budget', views.budget, name='budget'),
    path('budget/recent', views.budget_recent, name='budget/recent'),
    path('budget/new', views.new_transaction, name='budget/new'),
    path('budget/new_category', NewCategoryView.as_view(), name='budget/new_category'),
    path('budget/chart', views.chart, name='budget/chart'),
    path('budget/get_budget/', views.get_budget, name='get_budget'),
    path('budget/delete', views.delete, name='budget_delete'),
    path('budget/get_categories_budget', views.get_category_budget, name='get_category_budget'),
    path('budget/delete_category', views.delete_category, name='budget_delete_category')

]

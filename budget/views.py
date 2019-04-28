from django.shortcuts import render
from budget.models import Income


def base(request):
    income_list = Income.objects.order_by('-income_date')
    context = {'income_list': income_list}
    return render(request, 'budget/base.html', context)


def home(request):
    return render(request, 'budget/home.html')

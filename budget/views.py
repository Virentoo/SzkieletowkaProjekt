import datetime

from django.shortcuts import render
from budget.models import Transaction, Category


def base_recent(request):
    date = datetime.datetime.now()
    selected_id = request.POST.get('dropdown_panel', 1)
    context = {'date': date}

    if selected_id == "2":
        expense_list = Transaction.objects.filter(type="expense").order_by('-date')
        context['transaction_list'] = expense_list
        context['selected_panel'] = 'Expense'
    else:
        income_list = Transaction.objects.filter(type="income").order_by('-date')
        context['transaction_list'] = income_list
        context['selected_panel'] = 'Income'
    return render(request, 'budget/base_recent.html', context)


def home(request):
    return render(request, 'budget/home.html')


def base(request):
    category_list = Category.objects.order_by('-name')
    context = {'category_list': category_list}
    item_list = {}
    for item in category_list:
        item_list[item] = (Transaction.objects.filter(category=item))
    context['item_list'] = item_list
    return render(request, 'budget/base.html', context)

import datetime

from django.shortcuts import render
from budget.models import Transaction, Category
from django.contrib.auth.decorators import login_required


@login_required()
def base_recent(request):
    date = datetime.datetime.now()
    selected_id = request.POST.get('dropdown_panel', 1)
    user = request.user
    context = {'date': date}

    if selected_id == "2":
        expense_list = Transaction.objects.filter(category__user=user, type="expense").order_by('-date')
        context['transaction_list'] = expense_list
        context['selected_panel'] = 'Expense'
    else:
        income_list = Transaction.objects.filter(category__user=user, type="income").order_by('-date')
        context['transaction_list'] = income_list
        context['selected_panel'] = 'Income'
    return render(request, 'budget/base_recent.html', context)


def home(request):
    return render(request, 'budget/home.html')


@login_required()
def base(request):
    item_list = {}
    user = request.user
    category_list = Category.objects.filter(user=user).order_by('-name')
    context = {'category_list': category_list}
    for item in category_list:
        item_list[item] = (
            Transaction.objects.filter(category=item))
    context['item_list'] = item_list
    return render(request, 'budget/base.html', context)

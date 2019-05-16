import datetime

from django.shortcuts import render
from budget.models import Transaction, Category
from django.contrib.auth.decorators import login_required
from django.utils import timezone


@login_required()
def budget(request):
    item_list = {}
    user = request.user
    category_list = Category.objects.filter(user=user).order_by('-name')
    context = {'category_list': category_list}
    for item in category_list:
        item_list[item] = (
            Transaction.objects.filter(category=item))
    context['item_list'] = item_list
    return render(request, 'budget/budget.html', context)


@login_required()
def budget_recent(request):
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
    return render(request, 'budget/budget_recent.html', context)


@login_required()
def chart(request):
    user = request.user
    user_id = user.id
    category_list = Category.objects.filter(user=user).order_by('-name')
    categories = list()
    item_list = {}

    for category in category_list:
        categories.append(category.name)

    categories_id = list()
    for category in category_list:
        categories_id.append(category.id)

    user_transactions = []
    sums_list_current = []
    sums_list_previous = []

    for n in categories_id:
        user_transactions.append(Category.objects.get(id=n).transaction_set.all())

    for n in user_transactions:
        sum_current = 0
        sum_previous = 0
        for i in n:
            if i.type in ["expense", "Expense"]:
                if i.date >= timezone.now() - datetime.timedelta(days=30):
                    sum_current += i.amount
                if i.date <= timezone.now() - datetime.timedelta(days=30) and i.date >= timezone.now() - datetime.timedelta(days=60):
                    sum_previous += i.amount
        sums_list_current.append(sum_current)
        sums_list_previous.append(sum_previous)

    for item in category_list:
        item_list[item] = (
            Transaction.objects.filter(category=item))

    return render(request, 'budget/chart.html',{
        'categories': categories,
        'categories_id': categories_id,
        'item_list' : item_list,
        'sums_list_current' : sums_list_current,
        'sums_list_previous' : sums_list_previous,
    })

def home(request):
    return render(request, 'budget/home.html')

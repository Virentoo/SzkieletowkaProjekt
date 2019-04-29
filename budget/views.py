import datetime

from django.shortcuts import render
from budget.models import Income, Expense


def base(request):
    date = datetime.datetime.now()
    if request.method == "POST":
        selected_id = request.POST['dropdown_panel']
    else:
        selected_id = 1

    context = {'date': date}
    if selected_id == "2":
        expense_list = Expense.objects.order_by('-expense_date')
        context['expense_list'] = expense_list
        context['selected_panel'] = 'Expense'
        return render(request, 'budget/base_expense.html', context)
    else:
        income_list = Income.objects.order_by('-income_date')
        context['income_list'] = income_list
        context['selected_panel'] = 'Income'
        return render(request, 'budget/base_income.html', context)


def home(request):
    return render(request, 'budget/home.html')

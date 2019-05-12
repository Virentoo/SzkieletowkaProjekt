from django.shortcuts import render
from budget.models import Transaction, Category
from django.contrib.auth.decorators import login_required
from .forms import FilterForm
from .utils import convert_datetime
import datetime


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
    if 'transaction_type' in request.session:
        selected_id = request.session['transaction_type']
    else:
        selected_id = 1
    in_monthly = request.POST.get('monthly')
    if in_monthly == "":
        in_monthly = None

    user = request.user
    context = {'date': date}

    transaction_list = Transaction.objects.filter(category__user=user)
    if in_monthly:
        transaction_list = transaction_list.filter(category__monthly=in_monthly)
    if request.method == "POST":
        if 'dropdown_panel' in request.POST:
            selected_id = request.POST.get('dropdown_panel', 1)
            request.session['transaction_type'] = selected_id
        form = FilterForm(request.POST)
        if form.is_valid():
            priceFrom = form.cleaned_data['priceFrom']
            priceTo = form.cleaned_data['priceTo']
            dateFrom = form.cleaned_data['dateFrom']
            dateTo = form.cleaned_data['dateTo']
            timeFrom = form.cleaned_data['timeFrom']
            timeTo = form.cleaned_data['timeTo']
            recCategory = request.POST.get('recCategory', None)
            remCategory = request.POST.get('remCategory', None)
            datetimeFrom = convert_datetime(dateFrom, timeFrom)
            datetimeTo = convert_datetime(dateTo, timeTo)
            if priceFrom:
                transaction_list = transaction_list.filter(amount__gte=priceFrom)
            if priceTo:
                transaction_list = transaction_list.filter(amount__lte=priceTo)
            if datetimeFrom:
                transaction_list = transaction_list.filter(date__gte=datetimeFrom)
            if datetimeTo:
                transaction_list = transaction_list.filter(date__lte=datetimeTo)
            if recCategory:
                if 'selected_categories' in request.session:
                    category_ses = request.session['selected_categories']
                else:
                    category_ses = []
                if recCategory not in category_ses:
                    category_ses.append(recCategory)
                    request.session['selected_categories'] = category_ses
            elif remCategory:
                category_ses = request.session['selected_categories']
                if remCategory in category_ses:
                    category_ses.remove(remCategory)
                    request.session['selected_categories'] = category_ses
            if 'selected_categories' in request.session:
                category_ses = request.session['selected_categories']
                context['selected_categories'] = Category.objects.filter(pk__in=category_ses)
                if len(category_ses) > 0:
                    transaction_list = transaction_list.filter(category__pk__in=category_ses)
    else:
        form = FilterForm()
        request.session.delete('selected_categories')

    context['form'] = form
    context['categories'] = Category.objects.filter(user=user)
    if in_monthly:
        context['in_monthly'] = in_monthly
    if selected_id == "2":
        expense_list = transaction_list.filter(type="expense").order_by('-date')
        context['transaction_list'] = expense_list
        context['selected_panel'] = 'Expense'
    else:
        income_list = transaction_list.filter(type="income").order_by('-date')
        context['transaction_list'] = income_list
        context['selected_panel'] = 'Income'
    return render(request, 'budget/budget_recent.html', context)


def home(request):
    return render(request, 'budget/home.html')

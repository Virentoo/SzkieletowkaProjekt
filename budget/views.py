from django.shortcuts import render
from django.urls import reverse
from budget.models import Transaction, Category
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from .forms import FilterForm
from .utils import convert_datetime
from django.http import Http404
from django.http import HttpResponse
from django.utils import timezone
import datetime
from django.core import serializers


@login_required()
def budget(request):
    user = request.user

    categories = Category.objects.filter(user=user)
    categories_seri = serializers.serialize("json", categories)

    context = {'categories': categories_seri}

    return render(request, 'budget/budget.html', context)


@login_required()
def get_category_budget(request):
    if request.method != 'POST':
        raise Http404("Nein")

    user = request.user
    monthly = request.POST.get('monthly', '')
    sort_by = request.POST.get('sort_by', '1')
    category_ses = request.POST.getlist('selectedCategory', [])

    if sort_by == '1':
        sort_by = 'name'
    elif sort_by == '2':
        sort_by = '-name'

    context = {}

    items_list = {}
    category_list = Category.objects.filter(user=user).order_by(sort_by)

    if len(category_ses) > 0:
        category_list = category_list.filter(pk__in=category_ses)

    if monthly != '':
        category_list = category_list.filter(monthly=monthly)

    for item in category_list:
        items_list[item] = (
            Transaction.objects.filter(category=item))

    context['item_list'] = items_list
    context['category_list'] = category_list

    return render(request, 'budget/get_category_budget.html', context)


def home(request):
    return render(request, 'budget/home.html')


class NewTransactionView(CreateView):
    model = Transaction
    template_name = 'budget/new.html'
    fields = ['name', 'desc', 'type', 'category', 'date', 'amount']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('budget')


@login_required()
def new_expense(request):
    return render(request, 'budget/new.html')


@login_required()
def new_income(request):
    return render(request, 'budget/new_income.html')


class NewCategoryView(CreateView):
    model = Category
    template_name = 'budget/new_category.html'
    fields = ['name', 'monthly']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('budget')


@login_required()
def budget_recent(request):
    user = request.user

    categories = Category.objects.filter(user=user)
    categories_seri = serializers.serialize("json", categories)

    context = {'categories': categories_seri}

    return render(request, 'budget/budget_recent.html', context)


@login_required()
def get_budget(request):
    if request.method != 'POST':
        raise Http404("Nein")

    in_monthly = request.POST.get('monthly', '')
    sort_by = request.POST.get('sort_by', '1')
    transaction_type = request.POST.get('transaction_type', 3)
    user = request.user

    context = {}

    transaction_list = Transaction.objects.filter(category__user=user)

    if in_monthly != '':
        transaction_list = transaction_list.filter(category__monthly=in_monthly)

    category_ses = request.POST.getlist('selectedCategory', [])
    if len(category_ses) > 0:
        transaction_list = transaction_list.filter(category__pk__in=category_ses)

    form = FilterForm(request.POST)
    if form.is_valid():
        priceFrom = form.cleaned_data['priceFrom']
        priceTo = form.cleaned_data['priceTo']
        dateFrom = form.cleaned_data['dateFrom']
        dateTo = form.cleaned_data['dateTo']
        timeFrom = form.cleaned_data['timeFrom']
        timeTo = form.cleaned_data['timeTo']
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
    else:
        form = FilterForm()

    context['form'] = form

    if in_monthly:
        context['in_monthly'] = in_monthly

    if transaction_type == 2:
        transaction_list = transaction_list.filter(type="expense")
    elif transaction_type == 1:
        transaction_list = transaction_list.filter(type="income")

    if sort_by == '1':
        transaction_list = transaction_list.order_by('-date')
    elif sort_by == '2':
        transaction_list = transaction_list.order_by('date')
    elif sort_by == '3':
        transaction_list = transaction_list.order_by('-amount')
    elif sort_by == '4':
        transaction_list = transaction_list.order_by('amount')
    elif sort_by == '5':
        transaction_list = transaction_list.order_by('name')

    context['transaction_list'] = transaction_list
    return render(request, 'budget/get_budget.html', context)


def clear_filter(request):
    if not request.is_ajax():
        return
    request.session['selected_categories'] = None


def delete(request):
    if request.method != 'POST':
        raise Http404("Nein")
    id = request.POST.getlist('transaction_id')
    if not id:
        return HttpResponse("Wrong id")
    Transaction.objects.filter(category__user=request.user, id__in=id).delete()
    return HttpResponse("Success")


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

from django.shortcuts import render
from django.urls import reverse
from budget.models import Transaction, Category
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from .forms import FilterForm, NewTransactionForm
from .utils import convert_datetime, filter_transactions
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


# class NewTransactionView(CreateView):
#     model = Transaction
#     template_name = 'budget/new.html'
#     fields = ['name', 'desc', 'type', 'category', 'date', 'amount']
#
#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         return super().form_valid(form)
#
#     def get_success_url(self):
#         return reverse('budget')


@login_required()
def new_expense(request):
    return render(request, 'budget/new.html')


@login_required()
def new_income(request):
    return render(request, 'budget/new_income.html')


def new_transaction(request):
    if request.method  == 'POST':
        form = NewTransactionForm(request.user, request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return render(request, 'budget/budget.html')
    else:
        form = NewTransactionForm(request.user)
    return render(request, 'budget/new.html', {'form': form})


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

    user = request.user

    context = {}

    transaction_list = Transaction.objects.filter(category__user=user)
    transaction_list = filter_transactions(transaction_list, request.POST)

    form = FilterForm(request.POST)
    if not form.is_valid():
        form = FilterForm()

    in_monthly = request.POST.get('monthly')
    if in_monthly:
        context['in_monthly'] = in_monthly
    context['form'] = form
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


def delete_category(request):
    if request.method != 'POST':
        raise Http404("Nein")
    id = request.POST['category_id']
    if not id:
        return HttpResponse("Wrong id")
    Category.objects.filter(id__in=id).delete()
    return HttpResponse("Success")


@login_required()
def chart(request):
    user = request.user
    user_id = user.id
    category_list = Category.objects.filter(user=user).order_by('-name')
    categories = list()
    item_list = {}

    # Tutaj najpierw pobieram liste wszystkich tranzacji uzytkownika
    transaction_list = Transaction.objects.filter(category__user=user)
    # A potem przefiltrowuje ją
    # 'transaction_list' - list tranzakcji
    transaction_list = filter_transactions(transaction_list, request.GET)

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
                if i.date <= timezone.now() - datetime.timedelta(
                        days=30) and i.date >= timezone.now() - datetime.timedelta(days=60):
                    sum_previous += i.amount
        sums_list_current.append(sum_current)
        sums_list_previous.append(sum_previous)

    for item in category_list:
        item_list[item] = (
            Transaction.objects.filter(category=item))

    return render(request, 'budget/chart.html', {
        'categories': categories,
        'categories_id': categories_id,
        'item_list': item_list,
        'sums_list_current': sums_list_current,
        'sums_list_previous': sums_list_previous,
    })

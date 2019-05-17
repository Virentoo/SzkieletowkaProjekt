from django.shortcuts import render
from budget.models import Transaction, Category
from django.contrib.auth.decorators import login_required
from .forms import FilterForm
from .utils import convert_datetime
from django.http import Http404
from django.http import HttpResponse


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
    user = request.user

    context = {'categories': Category.objects.filter(user=user)}

    if 'selected_categories' in request.session:
        category_ses = request.session['selected_categories']
        context['selected_categories'] = Category.objects.filter(pk__in=category_ses)

    return render(request, 'budget/budget_recent.html', context)


def home(request):
    return render(request, 'budget/home.html')


def new_expense(request):
    return render(request, 'budget/new_expense.html')


def new_income(request):
    return render(request, 'budget/new_income.html')


@login_required()
def get_budget(request):
    if request.method != 'POST':
        raise Http404("Nein")

    in_monthly = request.POST.get('monthly')

    if in_monthly == "":
        in_monthly = None

    user = request.user
    context = {}

    reset_filter = request.POST.get('reset')
    if reset_filter and reset_filter == 'true' and 'selected_categories' in request.session:
        del request.session['selected_categories']

    transaction_type = 1

    transaction_list = Transaction.objects.filter(category__user=user)
    if in_monthly:
        transaction_list = transaction_list.filter(category__monthly=in_monthly)

    form = FilterForm(request.POST)
    if form.is_valid():
        transaction_type_str = form.cleaned_data['transaction_type']
        if transaction_type_str:
            transaction_type = int(transaction_type_str)
            request.session['transaction_type'] = transaction_type
        elif 'transaction_type' in request.session:
            transaction_type = request.session['transaction_type']
        priceFrom = form.cleaned_data['priceFrom']
        priceTo = form.cleaned_data['priceTo']
        dateFrom = form.cleaned_data['dateFrom']
        dateTo = form.cleaned_data['dateTo']
        timeFrom = form.cleaned_data['timeFrom']
        timeTo = form.cleaned_data['timeTo']
        recCategory = form.cleaned_data['recCategory']
        remCategory = form.cleaned_data['remCategory']
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
    if in_monthly:
        context['in_monthly'] = in_monthly
    if transaction_type == 2:
        transaction_list = transaction_list.filter(type="expense")
    elif transaction_type == 1:
        transaction_list = transaction_list.filter(type="income")

    sort_by = request.POST.get('sort_by', '1')

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


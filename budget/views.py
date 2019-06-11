import datetime

import reportlab
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.db.models import Sum
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import formats
from django.utils import timezone
from django.views.generic import CreateView
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from budget.models import Transaction, Category
from .forms import FilterForm, NewTransactionForm
from .utils import filter_transactions


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
        raise Http404("")

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


def new_transaction(request):
    if request.method == 'POST':
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
        raise Http404("")

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
        raise Http404("")
    id = request.POST.getlist('transaction_id')
    if not id:
        return HttpResponse("Wrong id")
    Transaction.objects.filter(category__user=request.user, id__in=id).delete()
    return HttpResponse("Success")


def delete_category(request):
    if request.method != 'POST':
        raise Http404("")
    id = request.POST['category_id']
    if not id:
        return HttpResponse("Wrong id")
    Category.objects.filter(id__in=id).delete()
    return HttpResponse("Success")


@login_required()
def chart(request):
    user = request.user
    category_list = list()
    categories = list()
    item_list = {}

    transaction_list = Transaction.objects.filter(category__user=user)
    transaction_list = filter_transactions(transaction_list, request.GET)

    for transaction in transaction_list:
        if (transaction.category not in category_list):
            category_list.append(transaction.category)

    for category in category_list:
        categories.append(category.name)

    categories_id = list()
    for category in category_list:
        categories_id.append(category.id)

    user_transactions = []
    for n in categories_id:
        transactions = list()
        for transaction in transaction_list:
            if (n == transaction.category.id):
                transactions.append(transaction)
        user_transactions.append(transactions)

    sums = []
    for n in user_transactions:
        sum = 0
        for i in n:
            if i.type in ["expense", "Expense"]:
                sum += i.amount
        sums.append(sum)

    for item in category_list:
        item_list[item] = (
            Transaction.objects.filter(category=item))

    return render(request, 'budget/chart.html', {
        'categories': categories,
        'sums': sums,
    })


@login_required()
def chart_unfiltred(request):
    user = request.user
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
                if i.date <= timezone.now() - datetime.timedelta(
                        days=30) and i.date >= timezone.now() - datetime.timedelta(days=60):
                    sum_previous += i.amount
        sums_list_current.append(sum_current)
        sums_list_previous.append(sum_previous)

    for item in category_list:
        item_list[item] = (
            Transaction.objects.filter(category=item))

    return render(request, 'budget/chart_unfiltred.html', {
        'categories': categories,
        'categories_id': categories_id,
        'item_list': item_list,
        'sums_list_current': sums_list_current,
        'sums_list_previous': sums_list_previous,
    })


def edit(request):
    transaction_id = request.POST.get('transaction_id')
    if not transaction_id:
        raise Http404('Wrong transaction id')
    transaction = Transaction.objects.filter(category__user=request.user, pk=transaction_id)[0]
    form = NewTransactionForm(request.user, request.POST)
    if form.is_valid():
        t = form.save(commit=False)
        t.pk = transaction.pk
        t.save()
        return budget_recent(request)
    else:
        form = NewTransactionForm(request.user, instance=transaction)

    return render(request, 'budget/edit.html', {'form': form, 'transaction_id': transaction_id})


def gen_pdf(request):
    reportlab.rl_config.TTFSearchPath.append(str(settings.BASE_DIR) + '/budget/static/budget')
    pdfmetrics.registerFont(TTFont('Calibri', 'Calibri.ttf'))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=budget.pdf'

    user = request.user

    transaction_list = Transaction.objects.filter(category__user=user)
    transaction_list = filter_transactions(transaction_list, request.GET)

    pdf = canvas.Canvas(response)

    x = 0
    topy = 800
    y = 800
    footSize = 50
    pdf.translate(x, topy)
    pdf.setFont("Times-Roman", 20)
    pdf.drawCentredString(4 * inch, 0, "Home Budget")
    addspacing = 20 * 1.4 + 20
    y -= addspacing
    pdf.translate(inch, -addspacing)

    income_list = transaction_list.filter(type='income')
    expense_list = transaction_list.filter(type='expense')

    pdf.setFont('Calibri', 20)
    pdf.drawString(-inch / 2, 0, 'Overall statistics')
    pdf.rect(-inch, -5, 4 * inch, 2, fill=1)
    addspacing = 25 * 1.4
    y -= addspacing
    pdf.translate(0, -addspacing)

    textobject = pdf.beginText()
    sumIncome = income_list.aggregate(Sum('amount')).get('amount__sum', 0)
    if not sumIncome:
        sumIncome = 0
    sumExpense = expense_list.aggregate(Sum('amount')).get('amount__sum', 0)
    if not sumExpense:
        sumExpense = 0
    textobject.setFont('Calibri', 12)
    textobject.textLine('Number of all transactions: %d' % len(transaction_list))
    textobject.textLine('Number of expenses: %d' % len(expense_list))
    textobject.textLine('Number of incomes: %d' % len(income_list))
    textobject.textLine('The amount of money spent: %dzł' % sumExpense)
    textobject.textLine('The amount of money received: %dzł' % sumIncome)
    textobject.textLine('Balance: %dzł' % (sumIncome - sumExpense))
    pdf.drawText(textobject)
    objsize = -(textobject.getY() - 20)
    y -= objsize
    pdf.translate(0, -objsize)

    if len(income_list) > 0:
        pdf.setFont('Calibri', 20)
        pdf.drawString(-inch / 2, 0, 'Incomes')
        pdf.rect(-inch, -5, 4 * inch, 2, fill=1)
        addspacing = 25 * 1.4
        y -= addspacing
        pdf.translate(0, -addspacing)

    i = 0
    for transaction in income_list:
        i += 1
        textobject = pdf.beginText()
        textobject.setFont("Calibri", 16)
        textobject.textLine("%d. %s" % (i, transaction.name))
        textobject.setFont("Calibri", 12)
        textobject.textLine("Category: %s" % transaction.category.name)
        textobject.textLine(
            "Data: %s %s" % (formats.date_format(transaction.date), formats.time_format(transaction.date)))
        textobject.textLine("Amount: %s" % transaction.amount)
        textobject.textLine("Description: %s" % transaction.desc)
        objsize = -(textobject.getY() - 20 * 1.2)
        y -= objsize
        if y - footSize < 0:
            pdf.showPage()
            pdf.translate(inch, topy)
            y = topy
        pdf.drawText(textobject)
        pdf.translate(0, -objsize)

    if y - inch - footSize < 0:
        pdf.showPage()
        pdf.translate(inch, topy)
        y = topy
    if len(expense_list) > 0:
        pdf.setFont('Calibri', 20)
        pdf.drawString(-inch / 2, 0, 'Expenses')
        pdf.rect(-inch, -5, 4 * inch, 2, fill=1)
        addspacing = 25 * 1.4
        y -= addspacing
        pdf.translate(0, -addspacing)

    i = 0
    for transaction in expense_list:
        i += 1
        textobject = pdf.beginText()
        textobject.setFont("Calibri", 16)
        textobject.textLine("%d. %s" % (i, transaction.name))
        textobject.setFont("Calibri", 12)
        textobject.textLine("Category: %s" % transaction.category.name)
        textobject.textLine(
            "Data: %s %s" % (formats.date_format(transaction.date), formats.time_format(transaction.date)))
        textobject.textLine("Price: %s" % transaction.amount)
        textobject.textLine("Description: %s" % transaction.desc)
        objsize = -(textobject.getY() - 25 * 1.2)
        y -= objsize
        if y - footSize < 0:
            pdf.showPage()
            pdf.translate(inch, topy)
            y = topy
        pdf.drawText(textobject)
        pdf.translate(0, -objsize)

    pdf.showPage()
    pdf.save()
    return response

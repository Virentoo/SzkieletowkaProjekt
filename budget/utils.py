import datetime


def convert_datetime(date, time):
    if date:
        if time:
            return datetime.datetime.combine(date, time)
        else:
            return date
    else:
        if time:
            return time
        else:
            return None


def filter_transactions(transactions, post):
    in_monthly = post.get('monthly', '')
    sort_by = post.get('sort_by', '1')
    transaction_type = post.get('transaction_type', 3)
    category_ses = post.getlist('selectedCategory', [])
    priceFrom = post.get('priceFrom')
    priceTo = post.get('priceTo')
    dateFrom = post.get('dateFrom')
    dateTo = post.get('dateTo')
    timeFrom = post.get('timeFrom')
    timeTo = post.get('timeTo')
    datetimeFrom = convert_datetime(dateFrom, timeFrom)
    datetimeTo = convert_datetime(dateTo, timeTo)

    # Price
    if priceFrom:
        transactions = transactions.filter(amount__gte=priceFrom)
    if priceTo:
        transactions = transactions.filter(amount__lte=priceTo)

    # Date
    if datetimeFrom:
        transactions = transactions.filter(date__gte=datetimeFrom)
    if datetimeTo:
        transactions = transactions.filter(date__lte=datetimeTo)

    # Selected categories
    if len(category_ses) > 0:
        transactions = transactions.filter(category__pk__in=category_ses)

    # Is monthly
    if in_monthly != '':
        transactions = transactions.filter(category__monthly=in_monthly)

    # Transactions type
    if transaction_type == 2:
        transactions = transactions.filter(type="expense")
    elif transaction_type == 1:
        transactions = transactions.filter(type="income")

    # Sort options
    if sort_by == '1':
        transactions = transactions.order_by('-date')
    elif sort_by == '2':
        transactions = transactions.order_by('date')
    elif sort_by == '3':
        transactions = transactions.order_by('-amount')
    elif sort_by == '4':
        transactions = transactions.order_by('amount')
    elif sort_by == '5':
        transactions = transactions.order_by('name')
    return transactions

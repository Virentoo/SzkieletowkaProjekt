from django.shortcuts import render


def base(request):
    return render(request, 'budget/base.html')


def home(request):
    return render(request, 'budget/home.html')
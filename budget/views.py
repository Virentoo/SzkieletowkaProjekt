from django.shortcuts import render
from django.http import HttpResponse


def base(request):
    return render(request, 'budget/base.html')


def home(request):
    return render(request, 'budget/home.html')
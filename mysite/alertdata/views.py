from django.shortcuts import render
from django.http import HttpResponse

def hello(request, name):
    return HttpResponse("<b>Hello " + name + "</b>")
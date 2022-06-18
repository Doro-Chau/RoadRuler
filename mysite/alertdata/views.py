from django.shortcuts import render
from django.http import HttpResponse
import os

from sympy import content

def hello(request, name):
    return HttpResponse("<b>Hello " + name + "</b>")

def verify_domain(request, file):
    workpath = os.path.dirname(os.path.abspath(__file__))
    f = open(os.path.join(workpath, file), 'r')
    response = HttpResponse(f, content_type='application/default')
    # response['Content_Type'] = 'text/plain'
    response['Content-Disposition'] = 'inline; filename="example.txt"'
    return HttpResponse(response)

def getData(request):
    if request.method == 'POST':
        id = request.POST['id']
        return HttpResponse(id)
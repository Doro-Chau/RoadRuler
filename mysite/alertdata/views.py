from django.shortcuts import render
from django.http import HttpResponse
import os, json
from django.core.files.storage import default_storage
import io
from sympy import content
from rest_framework.response import Response

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
        # print(request.POST)
        data = request.body
        # file = file.decode()
        print(type(data), data)
        file = io.BytesIO(data)
        workpath = os.path.dirname(os.path.abspath(__file__))
        file_name = default_storage.save(workpath, file)
        # return Response(data=None)
        return render(request, 'getDada.html')

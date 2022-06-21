from django.shortcuts import render
from django.http import HttpResponse
import os, json
from django.core.files.storage import default_storage
import io, folium
from sympy import content
from rest_framework.response import Response
from .models import Aircraft, Shelter, ShelterDisaster

def map(request):
    m = folium.Map(location = [23.467335, 120.966222], tiles = 'Stamen Terrain', zoom_start = 7, control_scale = True)
    aircraft = Aircraft.objects.all()
    
    taoyuan_shelter = Shelter.objects.all().filter(city__contains='桃園市')
    aircraft_location = [[x.longtitude, x.latitude] for x in aircraft]
    taoyuan_shelter = [[x.longtitude, x.latitude] for x in taoyuan_shelter]
    feature_group = folium.FeatureGroup(name = '桃園市')
    
    # taoyuan_shelter.add_to(feature_group)
    
    for i in range(len(taoyuan_shelter)):
        folium.Marker(location=taoyuan_shelter[i]).add_to(feature_group)
        # folium.Marker(location=aircraft_location[i]).add_to(m)
    feature_group.add_to(m)
    # folium.LayerControl().add_to(m)
    
    water = ShelterDisaster.objects.all().filter(disaster='海嘯').select_related('shelter')
    # print(shelters)
    feature_group = folium.FeatureGroup(name='海嘯避難所')
    for shelter in water:
        folium.Marker(location=[shelter.shelter.longtitude, shelter.shelter.latitude]).add_to(feature_group)
        # print(shelter, shelter.shelter_id, shelter.shelter.longtitude)
    feature_group.add_to(m)
    folium.LayerControl().add_to(m)
    m = m._repr_html_()
    context = {
        'map': m,
        'aircraft': aircraft
    }
    return render(request, 'map.html', context)

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
        str = "<?xml version=\"1.0\" encoding=\"utf-8\" ?> <Data><Status>{0}</Status></Data>"
        str = str.format("True")
        return HttpResponse(str)
        # return render(request, 'getData.html')

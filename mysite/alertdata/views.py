from django.shortcuts import render
from django.http import HttpResponse
import os, json
import hashlib
from django.core.files.storage import default_storage
import io, folium
from sympy import content
from rest_framework.response import Response
from .models import Aircraft, Shelter, ShelterDisaster, RealtimeAlert, AlertLocation
from datetime import datetime
import boto3
import xml.etree.ElementTree as ET

def map(request):
    # m = folium.Map(location = [23.467335, 120.966222], tiles = 'Stamen Terrain', zoom_start = 7, preferCanvas = True)
    # aircraft = Aircraft.objects.all()
    
    # taoyuan_shelter = Shelter.objects.all().filter(city__contains='桃園市')
    # aircraft_location = [[x.longtitude, x.latitude] for x in aircraft]
    # taoyuan_shelter = [[x.longtitude, x.latitude] for x in taoyuan_shelter]
    # feature_group = folium.FeatureGroup(name = '桃園市', show = False)
    
    # # taoyuan_shelter.add_to(feature_group)
    
    # for i in range(len(taoyuan_shelter)):
    #     folium.Marker(location=taoyuan_shelter[i]).add_to(feature_group)
    #     # folium.Marker(location=aircraft_location[i]).add_to(m)
    # feature_group.add_to(m)
    # # folium.LayerControl().add_to(m)
    
    # water = ShelterDisaster.objects.all().filter(disaster='海嘯').select_related('shelter')
    # # print(shelters)
    # feature_group = folium.FeatureGroup(name='海嘯避難所', show = False)
    # for shelter in water:
    #     folium.Marker(location=[shelter.shelter.longtitude, shelter.shelter.latitude]).add_to(feature_group)
    #     # print(shelter, shelter.shelter_id, shelter.shelter.longtitude)
    # feature_group.add_to(m)
    # folium.LayerControl().add_to(m)
    # m = m._repr_html_()
    # context = {
    #     'map': m,
    #     'aircraft': aircraft
    # }
    # return render(request, 'map.html', context)
    return render(request, 'map2.html')
def verify_domain(request, file):
    workpath = os.path.dirname(os.path.abspath(__file__))
    f = open(os.path.join(workpath, file), 'r')
    response = HttpResponse(f, content_type='application/default')
    # response['Content_Type'] = 'text/plain'
    response['Content-Disposition'] = 'inline; filename="example.txt"'
    return HttpResponse(response)

def getData(request):
    if request.method == 'POST':
        data = request.body
        file = io.BytesIO(data)
        #workpath = os.path.dirname(os.path.abspath(__file__))
        #filename = default_storage.save(workpath, file)
        
        workpath = 'mymap/realtime_alert/'
        now = datetime.now()
        now = now.strftime("%Y%m%d-%H-%M-%S")
        workpath = os.path.join(workpath, now)
        client = boto3.client('s3', aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'), aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
        response = client.put_object(Bucket='dorothybucket', Body=data, Key=workpath)

        root = ET.fromstring(data)
        dict_alert = {}
        for child in root:
            if len(child) == 0:
                dict_alert[child.tag[38:]] = child.text
        dict_alert = {k.lower(): v for k, v in dict_alert.items()}
        column_name = [x.name for x in RealtimeAlert._meta.get_fields()][2:]
        dict_alert = {x: dict_alert[x] for x in column_name}
        RealtimeAlert.objects.create(**dict_alert)
        
        for child in root:
            if len(child) != 0:
                alert_id = RealtimeAlert.objects.latest('alert_id').alert_id
                dict_location = {}
                dict_location['alert'] = alert_id
                for i in range(len(child)):
                    if len(child[i]) == 0:
                        dict_location[child[i].tag[38:]] = child[i].text
                        #print('layer2: ', child[i].tag[38:], child[i].text)
                        #print(dict_location)
                    else:
                        for j in range(len(child[i])):
                            if (child[i][j].tag[38:] != 'valueName') & (child[i][j].tag[38:] != 'value'):
                                dict_location[child[i][j].tag[38:]] = child[i][j].text
                                try:
                                    dict_location['location'] = dict_location['areaDesc']
                                except:
                                    pass
                            elif child[i][j].tag[38:] == 'valueName':
                                print('!!!!!!', child[i][j].text, child[i][j+1].text)
                                dict_location[child[i][j].text] = child[i][j+1].text
                            #print('layer3: ', child[i][j].tag[38:], child[i][j].text, len(child[i][j]))
                            #print(dict_location)
        
        dict_location = {k.lower(): v for k, v in dict_location.items()}
        column_name = [x.name for x in AlertLocation._meta.get_fields()]
        print(column_name)
        dict_location = {x: dict_location[x] for x in column_name}
            
        #AlertLocation.objects.create(**dict_location)
        str = "<?xml version=\"1.0\" encoding=\"utf-8\" ?> <Data><Status>{0}</Status></Data>"
        str = str.format("True")
        return HttpResponse(str)

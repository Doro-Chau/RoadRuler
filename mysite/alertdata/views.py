from requests import request
from .models import RealtimeAlert, AlertLocation, TrafficCctv, TrafficSection, TrafficLivecity, TrafficLivevd, TrafficLink, Parkinglot, Construction, ConstructionCoor, TrafficLinkBroken, MonitorRealtime, MonitorDaily, MonitorLogin
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os, io, json
import urllib
from django.core.files.storage import default_storage
from sympy import content
from rest_framework.response import Response
import boto3
import xml.etree.ElementTree as ET
import pandas as pd
from pymongo import MongoClient
import calendar
import datetime
from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from passlib.hash import sha256_crypt

@ensure_csrf_cookie
def map(request):
    return render(request, 'map2.html')

def monitor(request):
    hash = sha256_crypt.hash('358410018')
    if request.method == 'POST':
        data = list(MonitorLogin.objects.all().values())
        uname = request.POST.get('uname')
        psw = request.POST.get('psw')
        name = data[0]['user']
        password = data[0]['password']
        if uname == name and sha256_crypt.verify(psw, password):
            return render(request, 'monitor.html')
        else:
            context = {'state': 'incorrect password'}
            return render(request, 'signin.html', context)
    return render(request, 'signin.html')

def monitorAlert(request):
    df_alert = pd.DataFrame(list(RealtimeAlert.objects.all().values()))
    df_alert = df_alert[['sent', 'response']]
    df_alert.fillna('1', inplace=True)
    alert = df_alert.T.values.tolist()
    alert[1] = [2 if 'sender' in x else 1 for x in alert[1]]
    return HttpResponse(alert)

def monitorRealtime(request):
    df_realtime = pd.DataFrame(list(MonitorRealtime.objects.all().values()))
    realtime = df_realtime.values.tolist()
    return HttpResponse(realtime)

def monitorDaily(request):
    df_daily = pd.DataFrame(list(MonitorDaily.objects.all().values()))
    df_return = pd.DataFrame(columns=['date', 'cctv', 'park', 'vd'])
    for index, x in df_daily.iterrows():
        if index != 0:
            df_return = df_return.append({'date': df_daily.loc[index]['date'], 'cctv': df_daily.loc[index]['cctv'], 'park': df_daily.loc[index]['mongo_lot']-df_daily.loc[index-1]['mongo_lot'], 'vd': df_daily.loc[index]['mongo_vd']-df_daily.loc[index-1]['mongo_vd']}, ignore_index=True)
    df_return = df_return.astype({'date': str})
    list_return = df_return.values.tolist()
    return HttpResponse(list_return)

def processmaplot(weekday, mondata):
    df_mondata = pd.DataFrame(mondata)
    df_mondata = df_mondata.drop(columns=['_id']).drop_duplicates(subset=['update_time'])
    df_mondata[['weekday', 'month', 'date', 'time', 'CST', 'year']] = df_mondata['update_time'].str.split(' ', expand=True)
    df_mondata[['hr', 'min', 'sec']] = df_mondata['time'].str.split(':', expand=True)
    df_mondata = df_mondata.groupby(['hr', 'weekday']).agg({'totalcar': 'mean', 'availablecar': 'mean'}).reset_index()
    if (weekday != '平日') and (weekday != '假日'):
        df_mondata = df_mondata[df_mondata['weekday']==weekday]
    elif weekday == '假日':
        df_mondata = df_mondata[(df_mondata['weekday']=='Sat')|(df_mondata['weekday']=='Sun')]
        df_mondata['weekday'] = '假日'
        df_mondata = df_mondata.groupby(['hr', 'weekday']).agg({'totalcar': 'mean', 'availablecar': 'mean'}).reset_index()
    elif weekday == '平日':
        df_mondata = df_mondata[(df_mondata['weekday']!='Sat')&(df_mondata['weekday']!='Sun')]
        df_mondata['weekday'] = '平日'
        df_mondata = df_mondata.groupby(['hr', 'weekday']).agg({'totalcar': 'mean', 'availablecar': 'mean'}).reset_index()
    dict_lot = {}
    for index, x in df_mondata.iterrows():
        left_lot_amount = [x['hr']] * int(x['availablecar'])
        left_lot_amount = [int(x) for x in left_lot_amount]
        if x['weekday'] in dict_lot:
            dict_lot[x['weekday']].extend(left_lot_amount)
        else:
            dict_lot[x['weekday']] = left_lot_amount
    return dict_lot
def maplot(request):
    # db.lot_history.delete_many({'update_time':{'$exists':0}})
    # db.lot_history.delete_many({'update_time':99999})
    print(json.loads(request.body))
    lotid = json.loads(request.body)['lotid']
    if json.loads(request.body)['weekday'] != ('平日' or '假日'):
        weekday = json.loads(request.body)['weekday'][:3].capitalize()
    else:
        weekday = json.loads(request.body)['weekday']
    print('lotid', lotid, 'weekday', weekday)
    
    db, client = get_db_handle('traffic', os.getenv('MONGO_HOST'), 27017, os.getenv('MONGO_USERNAME'), os.getenv('MONGO_PWD'))
    mondata = list(db.lot_history.find({'id':str(lotid)}))
    if len(mondata) == 0:
        print('case1', mondata)
        return JsonResponse({'lot': {'weekday': []}}, status = 200)
    dict_lot = processmaplot(weekday, mondata)
    return JsonResponse({'lot': dict_lot}, status=200)

def get_db_handle(db_name, host, port, username, password):
    client = MongoClient(host = host, port = int(port), username = username, password = password)
    db = client[db_name]
    return db, client

def renderCctv(request):
    cctv = pd.DataFrame(list(TrafficCctv.objects.all().values()))
    cctv = cctv.values.tolist()
    # cctv = TrafficCctv.objects.filter(videostreamurl__isnull=False).filter(positionlat__isnull=False).filter(positionlon__isnull=False)
    # cctv = [[x.cctvid, x.city, x.videostreamurl, x.positionlat, x.positionlon] for x in cctv]
    return HttpResponse(cctv)

def renderLivevd(request):
    df_livevd = pd.DataFrame(list(TrafficLivevd.objects.all().values()))
    df_link = pd.DataFrame(list(TrafficLink.objects.all().values()))
    df_livevd.rename(columns={'linkid_id':'linkid'}, inplace=True)
    df_merge = df_link.merge(df_livevd, how = 'inner', on='linkid')
    df_merge[['startlon', 'startlat']] = df_merge['startpoint'].str.split(',', expand=True)
    df_merge[['midlon', 'midlat']] = df_merge['midpoint'].str.split(',', expand=True)
    df_merge[['endlon', 'endlat']] = df_merge['endpoint'].str.split(',', expand=True)
    df_merge = df_merge.drop(columns=['update_time_x', 'update_time_y', 'startpoint', 'midpoint', 'endpoint'])
    df_merge['speed'] = df_merge['speed'].astype(str)
    merge = df_merge.values.tolist()
    return HttpResponse(merge)

def renderLivecity(request):
    df_livecity = pd.DataFrame(list(TrafficLivecity.objects.all().values()))
    df_section = pd.DataFrame(list(TrafficSection.objects.all().values()))
    df_livecity.rename(columns={'sectionid_id':'sectionid'}, inplace=True)
    df_merge = df_livecity.merge(df_section, how='inner', on=['sectionid', 'city'])
    df_merge = df_merge[['city', 'sectionid', 'travelspeed', 'geometry']]
    merge = df_merge.values.tolist()
    return HttpResponse(merge)

def renderAlert(request):
    df_alert = pd.DataFrame(list(AlertLocation.objects.filter(expires__gt=(datetime.datetime.now()+datetime.timedelta(hours=8)), location__contains = '臺北').values()))
    df_alert = df_alert[['location', 'event', 'description']]
    df_alert = df_alert.drop_duplicates()
    alert = df_alert.values.tolist()
    return HttpResponse(alert)

def renderConstruction(reuest):
    df_construction = pd.DataFrame(list(Construction.objects.all().values()))
    df_construction_coor = pd.DataFrame(list(ConstructionCoor.objects.all().values()))
    df_construction_coor.rename(columns={'facility_no_id':'facility_no'}, inplace=True)
    df_merge = df_construction.merge(df_construction_coor, how='inner', on='facility_no')
    df_merge = df_merge[['contractor', 'construction_begin', 'construction_end', 'construction_timezone', 'lat', 'lon']]
    print(df_merge)
    merge = df_merge.values.tolist()
    return HttpResponse(merge)

def renderParking(request):
    df_parking = pd.DataFrame(list(Parkinglot.objects.all().values()))
    df_parking = df_parking[['id', 'name', 'totalcar', 'availablecar', 'entrancelat', 'entrancelon']]
    df_parking[df_parking['availablecar']!='無提供資料'] = df_parking[df_parking['availablecar']!='無提供資料'].astype({"availablecar": float})
    df_parking[df_parking['availablecar']!='無提供資料'] = df_parking[df_parking['availablecar']!='無提供資料'].astype({"availablecar": int})
    df_parking[df_parking['availablecar']!='無提供資料'] = df_parking[df_parking['availablecar']!='無提供資料'].astype({"availablecar": str})
    df_parking.loc[df_parking['availablecar'].str.contains('-', na=False), 'availablecar'] = '無提供資料'
    # df_parking = df_parking.drop(columns=['update_time', 'id', 'fareinfo', 'payex', 'address'])
    parking = df_parking.values.tolist()
    return HttpResponse(parking)

@csrf_exempt
def getData(request):
    if request.method == 'POST':
        data = request.body
        file = io.BytesIO(data)
        #workpath = os.path.dirname(os.path.abspath(__file__))
        #filename = default_storage.save(workpath, file)
        
        workpath = 'mymap/realtime_alert/'
        now = datetime.datetime.now()
        time_del = datetime.timedelta(hours=8) 
        now = now + time_del
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
        dict_alert['response'] = data
        column_name = [x.name for x in RealtimeAlert._meta.get_fields()][2:]
        dict_alert = {x: dict_alert[x] for x in column_name}
        RealtimeAlert.objects.create(**dict_alert)
        
        for child in root:
            if len(child) != 0:
                alert_id = RealtimeAlert.objects.latest('alert_id').alert_id
                dict_location = {}
                dict_location['alert'] = RealtimeAlert.objects.latest('alert_id')
                for i in range(len(child)):
                    if len(child[i]) == 0:
                        dict_location[child[i].tag[38:]] = child[i].text
                    else:
                        for j in range(len(child[i])):
                            if (child[i][j].tag[38:] != 'valueName') & (child[i][j].tag[38:] != 'value'):
                                dict_location[child[i][j].tag[38:]] = child[i][j].text
                                try:
                                    dict_location['location'] = dict_location['areaDesc']
                                except:
                                    pass
                            elif child[i][j].tag[38:] == 'valueName':
                                dict_location[child[i][j].text] = child[i][j+1].text
                            if 'location' in dict_location and j == 1:
                                dict_location = {k.lower(): v for k, v in dict_location.items()}
                                column_name = [x.name for x in AlertLocation._meta.get_fields()]
                                dict_location = {x: dict_location[x] for x in dict_location.keys() if x in column_name}
                                AlertLocation.objects.create(**dict_location)
        str = "<?xml version=\"1.0\" encoding=\"utf-8\" ?> <Data><Status>{0}</Status></Data>"
        str = str.format("True")
        return HttpResponse(str)

def error_404_view(request, exception):
   
    # we add the path to the the 404.html file
    # here. The name of our HTML file is 404.html
    return render(request, '404.html')

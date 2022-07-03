from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os, json, requests, sys
from numpy import append
import hashlib, math
from django.core.files.storage import default_storage
import io, folium
from sympy import content
from rest_framework.response import Response
from .models import Aircraft, Shelter, ShelterDisaster, RealtimeAlert, AlertLocation, TrafficCctv, TrafficSection, TrafficLivecity, TrafficLivevd, TrafficLink, Parkinglot, Construction, ConstructionCoor, TrafficLinkBroken
from datetime import datetime
import boto3
import xml.etree.ElementTree as ET
import pandas as pd
from django.db import transaction
from pymongo import MongoClient

def map(request):
    return render(request, 'map2.html')

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
    df_alert = pd.DataFrame(list(AlertLocation.objects.filter(expires__gt=datetime.now()).values()))
    df_alert = df_alert.drop(columns=['alert_id', 'severity_level', 'alert_critiria'])
    df_alert.to_csv('a.csv')
    print(df_alert)
    return HttpResponse(df_alert)

def renderConstruction(reuest):
    df_construction = pd.DataFrame(list(Construction.objects.all().values()))
    df_construction_coor = pd.DataFrame(list(ConstructionCoor.objects.all().values()))
    df_construction_coor.rename(columns={'facility_no_id':'facility_no'}, inplace=True)
    df_merge = df_construction.merge(df_construction_coor, how='inner', on='facility_no')
    df_merge = df_merge[['facility_no', 'contractor', 'road', 'lat', 'lon']]
    merge = df_merge.values.tolist()
    return HttpResponse(merge)

def getConstruction(request):
    ConstructionCoor.objects.all().delete()
    Construction.objects.all().delete()
    url = "https://tpnco.blob.core.windows.net/blobfs/Todaywork.json"
    response = requests.get(url)
    data = json.loads(response.content.decode('utf-8-sig'), strict=False)['features']
    construction = []
    constructioncoor = []
    aclist = []
    coorlist = []
    for d in data:
        if d['properties']['Ac_no'] not in aclist:
            aclist.append(d['properties']['Ac_no'])
            construction.append(Construction(d['properties']['Ac_no'], d['properties']['AppTime'], d['properties']['App_Name'], d['properties']['C_Name'], d['properties']['Addr'], d['properties']['Cb_Da'], d['properties']['Ce_Da'], d['properties']['Co_Ti']))
        for i in range(len(d['properties']['Positions'])):
            if isinstance(d['properties']['Positions'][i]['coordinates'][0], list):
                for coor in d['properties']['Positions'][i]['coordinates']:
                    coor_append = [d['properties']['Ac_no'], i, twd97_to_lonlat(coor[0], coor[1])[0], twd97_to_lonlat(coor[0], coor[1])[1]]
                    if coor_append not in coorlist:
                        coorlist.append(coor_append)
                        constructioncoor.append(ConstructionCoor(d['properties']['Ac_no'], i, twd97_to_lonlat(coor[0], coor[1])[0], twd97_to_lonlat(coor[0], coor[1])[1]))
            else:
                constructioncoor.append(ConstructionCoor(d['properties']['Ac_no'], i, twd97_to_lonlat(d['properties']['Positions'][i]['coordinates'][0], d['properties']['Positions'][i]['coordinates'][1])[0], twd97_to_lonlat(d['properties']['Positions'][i]['coordinates'][0], d['properties']['Positions'][i]['coordinates'][1])[1]))
    Construction.objects.bulk_create(construction)
    ConstructionCoor.objects.bulk_create(constructioncoor)
    return HttpResponse(response)

def getTraffic(request):
    url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/VD/City/Taipei"
    url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/VD/City/Taipei"
    url = 'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/City/Taipei'
    data = getApiResponse(request, url)
    data = json.loads(data.content.decode("utf-8"))
    # for i in data['VDLives']:
        # print(i.keys())
    
    return getApiResponse(request, url)

def getParking(request):
    bulk_create = []
    bulk_update = []
    exist_id = Parkinglot.objects.values_list('id', flat = True)
    # parking lot information
    parkingurl = "https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_alldesc.json"
    response_park = requests.get(parkingurl)
    parkdata = response_park.json()['data']
    # update_time = parkdata['UPDATETIME']
    df_park = pd.DataFrame(parkdata['park'])
    df_park["tw97x"] = pd.to_numeric(df_park["tw97x"])
    df_park["tw97y"] = pd.to_numeric(df_park["tw97y"])
    # df_park['update_time'] = update_time
    df_park = df_park[df_park['tw97x']>100]
    df_park = df_park.reset_index(drop=True)
    df_park[['entrancelat', 'entrancelon']] = ''
    for i in range(len(df_park)):
        df_park['entrancelat'][i], df_park['entrancelon'][i] = twd97_to_lonlat(df_park['tw97x'][i], df_park['tw97y'][i])

    # realtime available lot
    liveurl = "https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_allavailable.json"
    response = requests.get(liveurl)
    livedata = response.json()['data']
    update_time = livedata['UPDATETIME']
    df_live = pd.DataFrame(livedata['park'])
    df_live['update_time'] = update_time
    
    df_merge = df_park.merge(df_live, how='left', on='id')
    df_merge = df_merge[['update_time', 'id', 'area', 'name', 'summary', 'address', 'payex', 'serviceTime', 'totalcar', 'availablecar', 'entrancelat', 'entrancelon']]
    df_merge = df_merge.where(pd.notnull(df_merge), 99999)
    df_merge = df_merge[df_merge['entrancelat'] > 20]
    df_merge['name'] = df_merge['name'].str.replace(' ', '')
    # insert into mongo
    df_mongo = df_merge[['id', 'totalcar', 'availablecar']]
    db, client = get_db_handle('traffic', os.getenv('MONGO_HOST'), 27017, os.getenv('MONGO_USERNAME'), os.getenv('MONGO_PWD'))
    collection = db['lot_history']
    documents = df_mongo.T.to_dict().values()
    collection.insert_many(documents)

    parkinglot = Parkinglot.objects.all()
    for index, x in df_merge.iterrows():
        if x['id'] not in exist_id:
            bulk_create.append(Parkinglot(x['update_time'], x['id'], x['area'], x['name'], x['summary'], x['address'], x['payex'], x['serviceTime'], x['totalcar'], x['availablecar'], x['entrancelat'], x['entrancelon']))
            continue
        for pkl in parkinglot:        
            if pkl.pk == x['id']:
                pkl.update_time = x['update_time']
                pkl.area = x['area']
                pkl.name = x['name']
                pkl.summary = x['summary']
                pkl.address = x['address']
                pkl.payex = x['payex']
                pkl.servicetime = x['serviceTime']
                pkl.totalcar = x['totalcar']
                pkl.availablecar = x['availablecar']
                pkl.entrancelat = x['entrancelat']
                pkl.entrancelon = x['entrancelon']
                bulk_update.append(pkl)
    Parkinglot.objects.bulk_create(bulk_create)
    Parkinglot.objects.bulk_update(bulk_update, ['update_time', 'area', 'name', 'summary', 'address', 'payex', 'servicetime', 'totalcar', 'availablecar', 'entrancelat', 'entrancelon'])
    return HttpResponse(response)

def renderParking(request):
    df_parking = pd.DataFrame(list(Parkinglot.objects.all().values()))
    df_parking = df_parking[['name', 'totalcar', 'availablecar', 'entrancelat', 'entrancelon']]
    # df_parking = df_parking.drop(columns=['update_time', 'id', 'fareinfo', 'payex', 'address'])
    parking = df_parking.values.tolist()
    return HttpResponse(parking)

def get_db_handle(db_name, host, port, username, password):
    client = MongoClient(host = host, port = int(port), username = username, password = password)
    db = client[db_name]
    return db, client

def getLiveVD(request):
    db, client = get_db_handle('traffic', os.getenv('MONGO_HOST'), 27017, os.getenv('MONGO_USERNAME'), os.getenv('MONGO_PWD'))
    collection = db['vd_history']
    # information to be store or update
    bulk_update = []
    bulk_create = []

    # broken linkid
    broken_link = TrafficLinkBroken.objects.values_list('linkid', flat = True)
    # stoarable linkid
    storable_link = TrafficLink.objects.values_list('linkid', flat = True)
    # linkid already in live vd table
    existing_link = TrafficLivevd.objects.values_list('linkid', flat = True)
    
    url_liveVD = 'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/VD/City/Taipei'
    data_liveVD = json.loads(getApiResponse(request, url_liveVD).content.decode("utf-8"))
    update_time = data_liveVD['UpdateTime']
    for vdlive in data_liveVD['VDLives']:
        for linkflow in vdlive['LinkFlows']:
            for lane in linkflow['Lanes']:
                # 0. 擋下壞掉的 linkid
                if linkflow['LinkID'] in broken_link:
                    continue
                # 1. 正確性：-99 代表壞掉，對應的 linkid 不用存進表格，讓 link id table 蒐集對應資訊
                elif lane['Speed'] == -99.0:
                    continue
                # 2. 可行性：link id 不在現有 link id 中，要另外爬
                elif linkflow['LinkID'] not in storable_link:
                    url_link = f'https://tdx.transportdata.tw/api/basic/v2/Road/Link/LinkID/{linkflow["LinkID"]}'
                    getLink(request, url_link, linkflow['LinkID'])
                # 3. update or create
                elif linkflow['LinkID'] not in existing_link:
                    bulk_create.append([update_time, vdlive['VDID'], linkflow['LinkID'], lane['Speed']])
                elif linkflow['LinkID'] in existing_link:
                    bulk_update.append([update_time, vdlive['VDID'], linkflow['LinkID'], lane['Speed']])
    df_bulk_create = pd.DataFrame(bulk_create, columns = ['update_time', 'VDID', 'LinkID', 'Speed'])
    df_bulk_update = pd.DataFrame(bulk_update, columns = ['update_time', 'VDID', 'LinkID', 'Speed'])
    df_bulk_create = df_bulk_create[df_bulk_create['Speed']!=0]
    df_bulk_update = df_bulk_update[df_bulk_update['Speed']!=0]
    df_bulk_create = df_bulk_create.groupby(['LinkID']).agg({'update_time':'first', 'Speed':'mean'}).reset_index()
    df_bulk_update = df_bulk_update.groupby(['LinkID']).agg({'update_time':'first', 'Speed':'mean'}).reset_index()
    df_concat = pd.concat([df_bulk_update, df_bulk_create])
    
    # insert into mongo
    documents = df_concat.T.to_dict().values()
    collection.insert_many(documents)
    
    # bulk create
    df_bulk_create = [TrafficLivevd(x['update_time'], x['LinkID'], x['Speed']) for index, x in df_bulk_create.iterrows()]
    TrafficLivevd.objects.bulk_create(df_bulk_create)
    
    # bulk update
    bulk_update_list = []
    all_trafficlivd = TrafficLivevd.objects.all()
    for at in all_trafficlivd:
        for index, x in df_bulk_update.iterrows():
            if at.pk == x['LinkID']:
                at.update_time = x['update_time']
                at.speed = x['Speed']
                bulk_update_list.append(at)
    TrafficLivevd.objects.bulk_update(bulk_update_list, ['update_time', 'speed'])    
    return getApiResponse(request, url_liveVD)

def getLink(request, url, LinkID):
    print('Enter get link', LinkID)
    already_insert = TrafficLinkBroken.objects.values_list('linkid', flat = True)
    url_link = url
    insert_list = []
    linkid = []
    try:
        data_link = json.loads(getApiResponse(request, url_link).content.decode("utf-8"))
        print(data_link)
    except:
        data_link = []
        
    if data_link:
        insert = TrafficLink(data_link[0]['UpdateDate'], LinkID, data_link[0]['RoadName'], data_link[0]['StartPoint'], data_link[0]['MidPoint'], data_link[0]['EndPoint'])
        insert.save()
    elif LinkID not in already_insert:
        TrafficLinkBroken.objects.create(linkid=LinkID)
    return getApiResponse(request, url_link)


def getCCTV(request):
    url_CCTV = 'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/City/Taipei'
    data_CCTV = json.loads(getApiResponse(request, url_CCTV).content.decode("utf-8"))
    cctvid = TrafficCctv.objects.values_list('cctvid', flat = True)
    update_time = data_CCTV['UpdateTime']
    bulk_create = []
    bulk_update = []
    trafficcctv = TrafficCctv.objects.all()
    for dict_CCTV in data_CCTV['CCTVs']:
        dict_CCTV['update_time'] = data_CCTV['UpdateTime']
        if dict_CCTV['CCTVID'] not in cctvid:
            bulk_create.append(TrafficCctv(update_time, dict_CCTV['CCTVID'], dict_CCTV['VideoStreamURL'], dict_CCTV['PositionLon'], dict_CCTV['PositionLat'], dict_CCTV['RoadName']))
        else:
            for tc in trafficcctv:
                if tc.pk == dict_CCTV:
                    tc.update_time = update_time
                    tc.videostreamurl = dict_CCTV['VideoStreamURL']
                    tc.positionlat = dict_CCTV['PositionLat']
                    tc.positionlon = dict_CCTV['PositionLon']
                    tc.roadname = dict_CCTV['RoadName']               
                    bulk_update.append(tc)

    TrafficCctv.objects.bulk_create(bulk_create)
    TrafficCctv.objects.bulk_update(bulk_update, ['update_time', 'videostreamurl', 'positionlat', 'positionlon', 'roadname'])  
    return getApiResponse(request, url_CCTV)

def getSection(request):
    # TrafficSectionLink.objects.all().delete()
    TrafficSection.objects.all().delete()
    city_list = ['Taipei', 'NewTaipei', 'Keelung', 'Taoyuan', 'YilanCounty', 'Taichung', 'Tainan']
    df_all = pd.DataFrame(columns = ['update_time', 'SectionID', 'city', 'Geometry', 'SectionName', 'RoadID', 
    'RoadName', 'RoadClass', 'RoadDirection', 'RoadSection', 'SectionLength', 'SectionStart', 'SectionEnd'])
    # traffic_section table
    for city in city_list:
        url_section = f'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Section/City/{city}'
        url_shape = f'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/SectionShape/City/{city}'
        data_section = json.loads(getApiResponse(request, url_section).content.decode("utf-8"))
        data_shape = json.loads(getApiResponse(request, url_shape).content.decode("utf-8"))
        update_time = data_section['UpdateTime']
        print(city)
        if city == 'YilanCounty':
            for sections in data_section['Sections']:
                sections['SectionID'] = sections['SectionID'].split(':')[2]

        df_section = pd.DataFrame(data_section['Sections'])
        if city == "Taichung":
            df_section = df_section.drop_duplicates(subset = ['SectionID'])
            # df_section.to_csv('d.csv')
        df_shape = pd.DataFrame(data_shape['SectionShapes'])
        df_merge = df_section.merge(df_shape, how = 'outer', on = 'SectionID')
        df_merge['city'] = city
        df_merge['update_time'] = update_time
        df_all = pd.concat([df_all, df_merge], ignore_index=True)
        
    df_all = df_all.drop(['SectionMile'], axis=1)
    bulk_list2 = [TrafficSection(row['update_time'], row['SectionID'], row['city'], row['Geometry'], row['SectionName'], row['RoadID'], row['RoadName'], row['RoadClass'], row['RoadDirection'], row['RoadSection'], row['SectionLength'], row['SectionStart'], row['SectionEnd']) for index, row in df_all.iterrows()]
    exist_sectionid = [row['SectionID'] for index, row in df_all.iterrows()]
    TrafficSection.objects.bulk_create(bulk_list2)
    
    # traffic_section_link table
    # bulk_list = []
    # already_append_id = []
    # for city in city_list:
    #     print(city)
    #     url_link = f'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/SectionLink/City/{city}'
    #     data_link = json.loads(getApiResponse(request, url_link).content.decode("utf-8"))
    #     update_time = data_link['UpdateTime']
    #     for i in range(len(data_link['SectionLinks'])):
    #         for linkid_dict in data_link['SectionLinks'][i]['LinkIDs']:
    #             if (data_link['SectionLinks'][i]['SectionID'] in exist_sectionid) and (data_link['SectionLinks'][i]['SectionID'] not in already_append_id):
    #                 bulk_list.append(TrafficSectionLink(update_time, data_link['SectionLinks'][i]['SectionID'], linkid_dict['LinkID'], city))
    #                 already_append_id.append(data_link['SectionLinks'][i]['SectionID'])
    # TrafficSectionLink.objects.bulk_create(bulk_list)
    return getApiResponse(request, url_section)

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

def getAuthorizationHeader(request):
    url = 'https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token'
    header = {"content-type":"application/x-www-form-urlencoded"}
    data = {
        'grant_type': 'client_credentials',
        "client_id": os.getenv('TDX_CLIENT_ID'),
        "client_secret": os.getenv('TDX_CLIENT_SECRET')}
    r = requests.post(url, headers = header, data = data)
    if r.status_code == 200:
        return HttpResponse(r.json()['access_token'])
    return HttpResponse(json.dumps({'token': r}))

def getApiResponse(request, url):
    token = getAuthorizationHeader(request)
    token = token.content.decode("utf-8")
    headers = {'authorization': f'Bearer {token}'}
    response = requests.get(url, headers = headers)
    return HttpResponse(response)

def twd97_to_lonlat(x, y):
    a = 6378137
    b = 6356752.314245
    long_0 = 121 * math.pi / 180.0
    k0 = 0.9999
    dx = 250000
    dy = 0
    e = math.pow((1-math.pow(b, 2)/math.pow(a,2)), 0.5)
    x -= dx
    y -= dy
    M = y / k0
    mu = M / ( a*(1-math.pow(e, 2)/4 - 3*math.pow(e,4)/64 - 5 * math.pow(e, 6)/256))
    e1 = (1.0 - pow((1   - pow(e, 2)), 0.5)) / (1.0 +math.pow((1.0 -math.pow(e,2)), 0.5))
    j1 = 3*e1/2-27*math.pow(e1,3)/32
    j2 = 21 * math.pow(e1,2)/16 - 55 * math.pow(e1, 4)/32
    j3 = 151 * math.pow(e1, 3)/96
    j4 = 1097 * math.pow(e1, 4)/512
    fp = mu + j1 * math.sin(2*mu) + j2 * math.sin(4* mu) + j3 * math.sin(6*mu) + j4 * math.sin(8* mu)
    e2 = math.pow((e*a/b),2)
    c1 = math.pow(e2*math.cos(fp),2)
    t1 = math.pow(math.tan(fp),2)
    r1 = a * (1-math.pow(e,2)) / math.pow( (1-math.pow(e,2)* math.pow(math.sin(fp),2)), (3/2))
    n1 = a / math.pow((1-math.pow(e,2)*math.pow(math.sin(fp),2)),0.5)
    d = x / (n1*k0)
    q1 = n1* math.tan(fp) / r1
    q2 = math.pow(d,2)/2
    q3 = ( 5 + 3 * t1 + 10 * c1 - 4 * math.pow(c1,2) - 9 * e2 ) * math.pow(d,4)/24
    q4 = (61 + 90 * t1 + 298 * c1 + 45 * math.pow(t1,2) - 3 * math.pow(c1,2) - 252 * e2) * math.pow(d,6)/720
    lat = fp - q1 * (q2 - q3 + q4)
    q5 = d
    q6 = (1+2*t1+c1) * math.pow(d,3) / 6
    q7 = (5 - 2 * c1 + 28 * t1 - 3 * math.pow(c1,2) + 8 * e2 + 24 * math.pow(t1,2)) * math.pow(d,5) / 120
    lon = long_0 + (q5 - q6 + q7) / math.cos(fp)
    lat = (lat*180) / math.pi
    lon = (lon*180) / math.pi
    return [lat, lon]
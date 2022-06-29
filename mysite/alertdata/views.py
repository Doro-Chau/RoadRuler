from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os, json, requests, sys
from numpy import append
import hashlib, math
from django.core.files.storage import default_storage
import io, folium
from sympy import content
from rest_framework.response import Response
from .models import Aircraft, Shelter, ShelterDisaster, RealtimeAlert, AlertLocation, TrafficCctv, TrafficSection, TrafficLivecity, TrafficLivevd, TrafficLink, Parkinglot
from datetime import datetime
import boto3
import xml.etree.ElementTree as ET
import pandas as pd

def map(request):
    
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

def renderCctv(request):
    cctv = TrafficCctv.objects.filter(videostreamurl__isnull=False).filter(positionlat__isnull=False).filter(positionlon__isnull=False)
    cctv = [[x.cctvid, x.city, x.videostreamurl, x.positionlat, x.positionlon] for x in cctv]
    return HttpResponse(cctv)

def renderLivevd(request):
    df_livevd = pd.DataFrame(list(TrafficLivevd.objects.all().values()))
    df_link = pd.DataFrame(list(TrafficLink.objects.all().values()))
    df_livevd.rename(columns={'linkid_id':'linkid'}, inplace=True)
    df_livevd = df_livevd.groupby('linkid').agg({'city':'first', 'vdid': 'first', 'speed':'mean'}).reset_index()
    df_merge = df_link.merge(df_livevd, how = 'inner', on=['linkid', 'city'])
    df_merge[['startlon', 'startlat']] = df_merge['startpoint'].str.split(',', expand=True)
    df_merge[['endlon', 'endlat']] = df_merge['endpoint'].str.split(',', expand=True)
    df_merge = df_merge.drop(columns=['update_time', 'startpoint', 'endpoint'])
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

def getTraffic(request):
    url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/VD/City/Taipei"
    # data = getApiResponse(request, url)
    # data = json.loads(data.content.decode("utf-8"))
    
    return getApiResponse(request, url)

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

def getParking(request):
    Parkinglot.objects.all().delete()
    # parking lot information
    parkingurl = "https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_alldesc.json"
    response_park = requests.get(parkingurl)
    parkdata = response_park.json()['data']
    update_time = parkdata['UPDATETIME']
    df_park = pd.DataFrame(parkdata['park'])
    df_park["tw97x"] = pd.to_numeric(df_park["tw97x"])
    df_park["tw97y"] = pd.to_numeric(df_park["tw97y"])
    df_park['update_time'] = update_time
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
    
    df_merge = df_park.merge(df_live, how='left', on='id')
    df_merge = df_merge[['update_time', 'id', 'area', 'name', 'summary', 'address', 'tel', 'payex', 'serviceTime', 'totalcar', 'availablecar', 'FareInfo', 'entrancelat', 'entrancelon']]
    df_merge = df_merge.where(pd.notnull(df_merge), 99999)
    df_merge = df_merge[df_merge['entrancelat'] > 20]
    df_merge['name'] = df_merge['name'].str.replace(' ', '')
    bulk_list = [Parkinglot(x['update_time'], x['id'], x['area'], x['name'], x['summary'], x['address'], x['tel'], x['payex'], x['serviceTime'], x['totalcar'], x['availablecar'], x['FareInfo'], x['entrancelat'], x['entrancelon']) for index, x in df_merge.iterrows()]
    Parkinglot.objects.bulk_create(bulk_list)
    return HttpResponse(df_merge)

def renderParking(request):
    df_parking = pd.DataFrame(list(Parkinglot.objects.all().values()))
    df_parking = df_parking[['name', 'totalcar', 'availablecar', 'entrancelat', 'entrancelon']]
    # df_parking = df_parking.drop(columns=['update_time', 'id', 'fareinfo', 'payex', 'address'])
    parking = df_parking.values.tolist()
    return HttpResponse(parking)

def getLive(request):
    TrafficLivecity.objects.all().delete()
    TrafficLivevd.objects.all().delete()
    city_list = ['Taipei', 'NewTaipei', 'Keelung', 'Taoyuan', 'YilanCounty', 'Taichung', 'Tainan']
    # df_liveVD = pd.DataFrame(columns = ['update_time', 'city', 'VDID', 'linkid', 'laneid', 'lanetype', 'speed', 'occupancy'])
    # df_livecity = pd.DataFrame(columns = ['update_time', 'city', 'sectionid_id', 'traveltime', 'travelspeed', 'congestionlevelid', 'congestionlevel'])
    list_liveVD = []
    list_livecity = []
    linkid_list = TrafficLink.objects.values_list('linkid', flat=True)

    for city in city_list:
        url_liveVD = f'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/VD/City/{city}'
        data_liveVD = json.loads(getApiResponse(request, url_liveVD).content.decode("utf-8"))
        update_time = data_liveVD['UpdateTime']
        print(city)
        for i in range(len(data_liveVD['VDLives'])):
            if city == 'YilanCounty':
                data_liveVD['VDLives'][i]['VDID'] = data_liveVD['VDLives'][i]['VDID'].split(':')[2]
            for j in range(len(data_liveVD['VDLives'][i]['LinkFlows'])):       
                for k in data_liveVD['VDLives'][i]['LinkFlows'][j]['Lanes']:
                    if data_liveVD['VDLives'][i]['LinkFlows'][j]['LinkID'] in linkid_list:
                        list_liveVD.append(TrafficLivevd(update_time, city, data_liveVD['VDLives'][i]['VDID'], data_liveVD['VDLives'][i]['LinkFlows'][j]['LinkID'], k['LaneID'], k['LaneType'], k['Speed'], k['Occupancy']))
        url_livecity = f'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/City/{city}'
        data_livecity = json.loads(getApiResponse(request, url_livecity).content.decode("utf-8"))
        update_time = data_livecity['UpdateTime']
        sectionidlist = []
        for i in range(len(data_livecity['LiveTraffics'])):
            try:
                if city != 'YilanCounty':
                    list_livecity.append(TrafficLivecity(update_time, city, data_livecity['LiveTraffics'][i]['SectionID'], data_livecity['LiveTraffics'][i]['TravelTime'], data_livecity['LiveTraffics'][0]['TravelSpeed'], data_livecity['LiveTraffics'][0]['CongestionLevelID'], data_livecity['LiveTraffics'][0]['CongestionLevel']))
                else:
                    if data_livecity['LiveTraffics'][i]['SectionID'] in sectionidlist:
                        continue
                    else:
                        sectionidlist.append(data_livecity['LiveTraffics'][i]['SectionID'])
                        list_livecity.append(TrafficLivecity(update_time, city, data_livecity['LiveTraffics'][i]['SectionID'], data_livecity['LiveTraffics'][i]['TravelTime'], data_livecity['LiveTraffics'][0]['TravelSpeed'], data_livecity['LiveTraffics'][0]['CongestionLevelID'], data_livecity['LiveTraffics'][0]['CongestionLevel']))
            except:
                pass
    TrafficLivecity.objects.bulk_create(list_livecity)
    TrafficLivevd.objects.bulk_create(list_liveVD)
    return getApiResponse(request, url_livecity)

def getLink(request):
    TrafficLink.objects.all().delete()
    city_list = ['Taipei', 'NewTaipei', 'Keelung', 'Taoyuan', 'YilanCounty', 'Taichung', 'Tainan']
    linkid_list = []
    for city in city_list:
        url_liveVD = f'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/VD/City/{city}'
        data_liveVD = json.loads(getApiResponse(request, url_liveVD).content.decode("utf-8"))
        for i in data_liveVD['VDLives']:
            for j in i['LinkFlows']:
                linkid_list.append(j['LinkID'])
    print(len(linkid_list))
    linkid_list = list(dict.fromkeys(linkid_list))
    print(len(linkid_list))
    insert_list = []
    linkid = []
    for LinkID in linkid_list:
        url_link = f'https://tdx.transportdata.tw/api/basic/v2/Road/Link/LinkID/{LinkID}'
        try:
            data_link = json.loads(getApiResponse(request, url_link).content.decode("utf-8"))
        except:
            print('decode error')
        try:
            insert_list.append(TrafficLink(data_link[0]['UpdateDate'], LinkID, data_link[0]['RoadName'], data_link[0]['StartPoint'], data_link[0]['EndPoint'], data_link[0]['City']))
            linkid.append(LinkID)
        except:
            print(data_link)
    print(insert_list, len(insert_list), insert_list[0])
    print(len(linkid))
    linkid = list(dict.fromkeys(linkid))
    print(len(linkid))
    TrafficLink.objects.bulk_create(insert_list)
    return getApiResponse(request, url_link)


def getCCTV(request):
    TrafficCctv.objects.all().delete()
    city_list = ['Taipei', 'NewTaipei', 'Keelung', 'Taoyuan', 'YilanCounty', 'Taichung', 'Tainan', 'Kaohsiung', 'TaitungCounty']
    for city in city_list:
        url_CCTV = f'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/City/{city}'
        data_CCTV = json.loads(getApiResponse(request, url_CCTV).content.decode("utf-8"))
        update_time = data_CCTV['UpdateTime']
        bulk_list = []
        print(city)
        for dict_CCTV in data_CCTV['CCTVs']:
            dict_CCTV['update_time'] = data_CCTV['UpdateTime']
            dict_CCTV['city'] = city
            dict_CCTV = {k.lower(): v for k, v in dict_CCTV.items()}
            column_name = [x.name for x in TrafficCctv._meta.get_fields()]
            dict_CCTV = {x: dict_CCTV[x] for x in dict_CCTV.keys() if x in column_name}
            if len(dict_CCTV.keys()) == 13:
                bulk_list.append(TrafficCctv(dict_CCTV['update_time'], dict_CCTV['city'], dict_CCTV['cctvid'], dict_CCTV['linkid'], dict_CCTV['videostreamurl'], dict_CCTV['locationtype'], dict_CCTV['positionlon'], dict_CCTV['positionlat'], dict_CCTV['surveillancetype'], dict_CCTV['roadid'], dict_CCTV['roadname'], dict_CCTV['roadclass'], dict_CCTV['roaddirection']))
            else:
                TrafficCctv.objects.create(**dict_CCTV)
        TrafficCctv.objects.bulk_create(bulk_list)
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
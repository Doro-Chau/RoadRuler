from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os, json, requests
from numpy import append
import hashlib
from django.core.files.storage import default_storage
import io, folium
from sympy import content
from rest_framework.response import Response
from .models import Aircraft, Shelter, ShelterDisaster, RealtimeAlert, AlertLocation, TrafficCctv, TrafficSection, TrafficLivecity, TrafficLivevd, TrafficLink
from datetime import datetime
import boto3
import xml.etree.ElementTree as ET
import pandas as pd

def map(request):
    
    # print(data3['UpdateTime'], data3['UpdateInterval'], data3['SrcUpdateTime'], data3['SrcUpdateInterval'], data3['AuthorityCode'])
    # for i in range(len(data3['VDs'])):
    #     print(data3['VDs'][i]['PositionLon'], data3['VDs'][0]['PositionLat'])
    #     print(data3['VDs'][i].keys())
    # for i in range(3):
    #     print(data['LiveTraffics'][i])
    # print(data2['Sections'][0]['SectionStart'], data2['Sections'][0]['SectionEnd'])
    
    m = folium.Map(location = [23.467335, 120.966222], tiles = 'Stamen Terrain', zoom_start = 7, preferCanvas = True)
    # print(len(data2['Sections']))
    # for i in range(len(data2['Section'])):
    #     print(i, data2['Sections'][i])
    #     print(data2['Sections'][i]['SectionStart']['PositionLat'], data2['Sections'][i]['SectionStart']['PositionLon']), (data2['Sections'][i]['SectionEnd']['PositionLat'], data2['Sections'][i]['SectionEnd']['PositionLon'])
    #     folium.PolyLine([(data2['Sections'][i]['SectionStart']['PositionLat'], data2['Sections'][i]['SectionStart']['PositionLon']), (data2['Sections'][i]['SectionEnd']['PositionLat'], data2['Sections'][i]['SectionEnd']['PositionLon'])]).add_to(m)
    aircraft = Aircraft.objects.all()
    
    taoyuan_shelter = Shelter.objects.all().filter(city__contains='桃園市')
    aircraft_location = [[x.longtitude, x.latitude] for x in aircraft]
    taoyuan_shelter = [[x.longtitude, x.latitude] for x in taoyuan_shelter]
    feature_group = folium.FeatureGroup(name = '桃園市', show = False)
    
    # taoyuan_shelter.add_to(feature_group)
    
    for i in range(len(taoyuan_shelter)):
        folium.Marker(location=taoyuan_shelter[i]).add_to(feature_group)
        # folium.Marker(location=aircraft_location[i]).add_to(m)
    feature_group.add_to(m)
    # folium.LayerControl().add_to(m)
    
    water = ShelterDisaster.objects.all().filter(disaster='海嘯').select_related('shelter')
    # print(shelters)
    feature_group = folium.FeatureGroup(name='海嘯避難所', show = False)
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
    # return render(request, 'map.html', context)
    return render(request, 'map2.html')

def getTraffic(request):
    url = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/VD/City/Taipei"
    url3 = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/City/Taichung"
    url4 = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/VD/City/Taichung"
    url7 = "https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CongestionLevel/City/Taipei"
    url2 = 'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/SectionLink/City/Taichung'
    url5 = "https://tdx.transportdata.tw/api/basic/v2/Road/Link/LinkID/6350570600020H"
    # data = getApiResponse(request, url)
    # data = json.loads(data.content.decode("utf-8"))
    # data3 = getApiResponse(request, url3)
    # data3 = json.loads(data3.content.decode("utf-8"))
    # data4 = getApiResponse(request, url4)
    # data4 = json.loads(data4.content.decode("utf-8"))
    # data7 = getApiResponse(request, url7)
    # data7 = json.loads(data7.content.decode("utf-8"))
    # print(data.keys())
    # print(data['VDs'][0].keys())
    # print(data3.keys())
    # print(data3['LiveTraffics'])
    # print(data7.keys())
    # print(data7['CongestionLevels'][0].keys())
    # print(data4.keys())
    # print(data4['VDLives'][0].keys())
    
    return getApiResponse(request, url5)

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
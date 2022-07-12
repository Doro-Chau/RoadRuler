import requests, json, math, os, sys, django
sys.path.append('/home/ec2-user/Project_disaster_map/mysite/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
#if __name__ == '__main__':
 #   import django
  #  django.setup()
django.setup()
sys.path.append('/home/ec2-user/Project_disaster_map/mysite/alertdata/')
from alertdata import models
from django.http import HttpResponse
#from models import Construction, ConstructionCoor, Parkinglot, TrafficLink, TrafficLinkBroken, TrafficLivevd, TrafficCctv
import pandas as pd
from pymongo import MongoClient

def getConstruction():
    models.ConstructionCoor.objects.all().delete()
    models.Construction.objects.all().delete()
    url = "https://tpnco.blob.core.windows.net/blobfs/Todaywork.json"
    response = requests.get(url)
    
    data = json.loads(response.content.decode('utf-8-sig'))['features']
    construction = []
    constructioncoor = []
    aclist = []
    coorlist = []
    for d in data:
        if d['properties']['Ac_no'] not in aclist:
            aclist.append(d['properties']['Ac_no'])
            construction.append(models.Construction(d['properties']['Ac_no'], d['properties']['AppTime'], d['properties']['App_Name'], d['properties']['C_Name'], d['properties']['Addr'], d['properties']['Cb_Da'], d['properties']['Ce_Da'], d['properties']['Co_Ti']))
        for i in range(len(d['properties']['Positions'])):
            if isinstance(d['properties']['Positions'][i]['coordinates'][0], list):
                for coor in d['properties']['Positions'][i]['coordinates']:
                    coor_append = [d['properties']['Ac_no'], i, twd97_to_lonlat(coor[0], coor[1])[0], twd97_to_lonlat(coor[0], coor[1])[1]]
                    if coor_append not in coorlist:
                        coorlist.append(coor_append)
                        constructioncoor.append(models.ConstructionCoor(d['properties']['Ac_no'], i, twd97_to_lonlat(coor[0], coor[1])[0], twd97_to_lonlat(coor[0], coor[1])[1]))
            else:
                constructioncoor.append(models.ConstructionCoor(d['properties']['Ac_no'], i, twd97_to_lonlat(d['properties']['Positions'][i]['coordinates'][0], d['properties']['Positions'][i]['coordinates'][1])[0], twd97_to_lonlat(d['properties']['Positions'][i]['coordinates'][0], d['properties']['Positions'][i]['coordinates'][1])[1]))
    models.Construction.objects.bulk_create(construction)
    models.ConstructionCoor.objects.bulk_create(constructioncoor)
    return response


def getParking():
    bulk_create = []
    bulk_update = []
    exist_id = models.Parkinglot.objects.values_list('id', flat = True)
    # parking lot information
    parkingurl = "https://tcgbusfs.blob.core.windows.net/blobtcmsv/TCMSV_alldesc.json"
    response_park = requests.get(parkingurl)
    print('responsepark', response_park)
    print(type(response_park))
    parkdata = response_park.json()['data']
    df_park = pd.DataFrame(parkdata['park'])
    df_park["tw97x"] = pd.to_numeric(df_park["tw97x"])
    df_park["tw97y"] = pd.to_numeric(df_park["tw97y"])
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
    df_merge = df_merge.astype({"availablecar": int})
    df_merge = df_merge.where(pd.notnull(df_merge), '無提供資料')
    df_merge = df_merge[df_merge['entrancelat'] > 20]
    df_merge['name'] = df_merge['name'].str.replace(' ', '')
    # insert into mongo
    df_mongo = df_merge[df_merge['update_time'].str.contains('CST')][['id', 'update_time', 'totalcar', 'availablecar']]
    db, client = get_db_handle('traffic', os.getenv('MONGO_HOST'), 27017, os.getenv('MONGO_USERNAME'), os.getenv('MONGO_PWD'))
    collection = db['lot_history']
    documents = df_mongo.T.to_dict().values()
    collection.insert_many(documents)

    parkinglot = models.Parkinglot.objects.all()
    for index, x in df_merge.iterrows():
        if x['id'] not in exist_id:
            bulk_create.append(models.Parkinglot(x['update_time'], x['id'], x['area'], x['name'], x['summary'], x['address'], x['payex'], x['serviceTime'], x['totalcar'], x['availablecar'], x['entrancelat'], x['entrancelon']))
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
    models.Parkinglot.objects.bulk_create(bulk_create)
    models.Parkinglot.objects.bulk_update(bulk_update, ['update_time', 'area', 'name', 'summary', 'address', 'payex', 'servicetime', 'totalcar', 'availablecar', 'entrancelat', 'entrancelon'])
    return response

def get_db_handle(db_name, host, port, username, password):
    client = MongoClient(host = host, port = int(port), username = username, password = password)
    db = client[db_name]
    return db, client


def getLiveVD():
    db, client = get_db_handle('traffic', os.getenv('MONGO_HOST'), 27017, os.getenv('MONGO_USERNAME'), os.getenv('MONGO_PWD'))
    collection = db['vd_history']
    # information to be store or update
    bulk_update = []
    bulk_create = []

    # broken linkid
    broken_link = models.TrafficLinkBroken.objects.values_list('linkid', flat = True)
    # stoarable linkid
    storable_link = models.TrafficLink.objects.values_list('linkid', flat = True)
    # linkid already in live vd table
    existing_link = models.TrafficLivevd.objects.values_list('linkid', flat = True)
    
    url_liveVD = 'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/Live/VD/City/Taipei'
    data_liveVD = json.loads(getApiResponse(url_liveVD).content.decode("utf-8"))
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
                    getLink(url_link, linkflow['LinkID'])
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
    df_bulk_create = [models.TrafficLivevd(x['update_time'], x['LinkID'], x['Speed']) for index, x in df_bulk_create.iterrows()]
    models.TrafficLivevd.objects.bulk_create(df_bulk_create)
    
    # bulk update
    bulk_update_list = []
    all_trafficlivd = models.TrafficLivevd.objects.all()
    for at in all_trafficlivd:
        for index, x in df_bulk_update.iterrows():
            if at.pk == x['LinkID']:
                at.update_time = x['update_time']
                at.speed = x['Speed']
                bulk_update_list.append(at)
    models.TrafficLivevd.objects.bulk_update(bulk_update_list, ['update_time', 'speed'])    
    return getApiResponse(url_liveVD)

def getLink(url, LinkID):
    already_insert = models.TrafficLinkBroken.objects.values_list('linkid', flat = True)
    url_link = url
    insert_list = []
    linkid = []
    try:
        data_link = json.loads(getApiResponse(url_link).content.decode("utf-8"))
    except:
        data_link = []
        
    if data_link:
        insert = models.TrafficLink(data_link[0]['UpdateDate'], LinkID, data_link[0]['RoadName'], data_link[0]['StartPoint'], data_link[0]['MidPoint'], data_link[0]['EndPoint'])
        insert.save()
    elif LinkID not in already_insert:
        models.TrafficLinkBroken.objects.create(linkid=LinkID)
    return getApiResponse(url_link)


def getCCTV():
    url_CCTV = 'https://tdx.transportdata.tw/api/basic/v2/Road/Traffic/CCTV/City/Taipei'
    data_CCTV = json.loads(getApiResponse(url_CCTV).content.decode("utf-8"))
    cctvid = models.TrafficCctv.objects.values_list('cctvid', flat = True)
    update_time = data_CCTV['UpdateTime']
    bulk_create = []
    bulk_update = []
    trafficcctv = models.TrafficCctv.objects.all()
    for dict_CCTV in data_CCTV['CCTVs']:
        dict_CCTV['update_time'] = data_CCTV['UpdateTime']
        if dict_CCTV['CCTVID'] not in cctvid:
            bulk_create.append(models.TrafficCctv(update_time, dict_CCTV['CCTVID'], dict_CCTV['VideoStreamURL'], dict_CCTV['PositionLon'], dict_CCTV['PositionLat'], dict_CCTV['RoadName']))
        else:
            for tc in trafficcctv:
                if tc.pk == dict_CCTV:
                    tc.update_time = update_time
                    tc.videostreamurl = dict_CCTV['VideoStreamURL']
                    tc.positionlat = dict_CCTV['PositionLat']
                    tc.positionlon = dict_CCTV['PositionLon']
                    tc.roadname = dict_CCTV['RoadName']               
                    bulk_update.append(tc)

    models.TrafficCctv.objects.bulk_create(bulk_create)
    models.TrafficCctv.objects.bulk_update(bulk_update, ['update_time', 'videostreamurl', 'positionlat', 'positionlon', 'roadname'])  
    return getApiResponse(url_CCTV)

def getAuthorizationHeader():
    url = 'https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token'
    header = {"content-type":"application/x-www-form-urlencoded"}
    data = {
        'grant_type': 'client_credentials',
        "client_id": os.getenv('TDX_CLIENT_ID'),
        "client_secret": os.getenv('TDX_CLIENT_SECRET')}
    r = requests.post(url, headers = header, data = data)
    if r.status_code == 200:
        return r.json()['access_token']
    return HttpResponse(json.dumps({'token': r}))

def getApiResponse(url):
    token = getAuthorizationHeader()
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

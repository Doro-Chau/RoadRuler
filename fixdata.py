from dotenv import load_dotenv
import os
import pymysql
import pandas as pd
import pymysql
import sqlalchemy
import wget, requests, glob
from pandas_ods_reader import read_ods

load_dotenv()
NCDR_KEY = os.getenv('NCDR_KEY')
SQL_HOST = os.getenv('SQL_HOST')
SQL_USER = os.getenv('SQL_USER')
SQL_PWD = os.getenv('SQL_PWD')
db = pymysql.connect(host=SQL_HOST, user=SQL_USER, password=SQL_PWD, database='myMap')
my_cursor = db.cursor()
engine = sqlalchemy.create_engine(f'mysql+pymysql://{SQL_USER}:{SQL_PWD}@{SQL_HOST}:{3306}/myMap')

df_all_disaster = pd.read_csv('./data source/避難所/4ca4767ee730031c5ca88fe7235daad1_export.csv')
df_all_disaster.columns = ['shelter_id', 'city', 'village', 'address', 'longtitude', 'latitude', 'name', 'accept_village', 'capacity', 'disaster', 'manager_name', 'manager_phone', 'indoor', 'outdoor', 'suitable_for_weak']
df_shelter = df_all_disaster.drop(['disaster', 'accept_village'], axis=1)
# df_shelter.to_sql('shelter',engine, if_exists='append', index=False)
df_suitable_disaster = df_all_disaster[['shelter_id', 'disaster']]
df_village = df_all_disaster[['shelter_id', 'accept_village']]

def multi_to_single(df, columns, spl):
    df_insert = pd.DataFrame(columns=columns)
    for i in range(len(df)):
        if pd.isna(df[columns[1]][i]):
            df_temp = pd.DataFrame([[df['shelter_id'][i], '未註明']], columns=columns)
            df_insert = pd.concat([df_insert, df_temp], ignore_index=True)
        else:
            try:
                disaster_list = df[columns[1]][i].split(spl)
                disaster_list = list(dict.fromkeys(disaster_list))
                for j in range(len(disaster_list)):
                    df_temp = pd.DataFrame([[df['shelter_id'][i], disaster_list[j]]], columns=columns)
                    df_insert = pd.concat([df_insert, df_temp], ignore_index=True)
            except:
                df_temp = pd.DataFrame([[df['shelter_id'][i], df[columns[1]][i]]], columns=columns)
                df_insert = pd.concat([df_insert, df_temp], ignore_index=True)
    return df_insert
# df_insert = multi_to_single(df_suitable_disaster, ['shelter_id', 'disaster'], ',')
# df_insert.to_sql('shelter_disaster',engine, if_exists='append', index=False)
# df_insert = multi_to_single(df_village, ['shelter_id', 'accept_village'], '、')
# df_insert.to_sql('shelter_accept_village',engine, if_exists='append', index=False)

df_nuclear = pd.read_csv('./data source/避難所/nuclear.csv')
# print(df_nuclear)
def getShelter():
    df_aircraft = pd.read_csv('./data source/避難所/aircraft/export1655299793.csv')
    df_aircraft = df_aircraft[~df_aircraft['資料集名稱'].str.contains('警察')]
    df_aircraft.reset_index(inplace=True)
    for i in range(len(df_aircraft)):
        url = df_aircraft['資料下載網址'][i]
        if ';' in url:
            url = url.split(';')[0]
        print(i, df_aircraft['資料集名稱'][i], url)

        try:
            response = requests.get(url)
        except:
            response = requests.get(url, verify=False)
        open('D:/appworks/Project/Project_disaster_map/data source/避難所/aircraft/'+df_aircraft['資料集名稱'][i]+'.csv','wb').write(response.content)
# getShelter()

# a = pd.read_csv('./data source/避難所/aircraft/南投縣防空疏散避難設施地點.csv')
# a = pd.read_csv('./data source/避難所/aircraft/臺南市防空疏散避難設施位置.csv')
# a = read_ods('./data source/避難所/aircraft/基隆市防空疏散避難設施.ods')
# print(a)
files = glob.glob("./data source/避難所/aircraft/*")
df_all = pd.DataFrame(columns = ['category', 'number', 'village', 'address', 'longtitude', 'latitude', 'basement', 'capacity', 'unit', 'note', 'city'])
for f in files:
    print(f)
    if '基隆' in f:
        df = read_ods(f)
        df = df.dropna(how='all')
        df['備註'] = ""
    else:
        try:
            df=pd.read_csv(f)
            df = df.dropna(how='all')
        except:
            df= pd.read_csv(f, encoding='ANSI')
            df = df.dropna(how='all')
    
    if len(df.columns) == 10:
        df.columns = ['category', 'number', 'village', 'address', 'latitude', 'longtitude', 'basement', 'capacity', 'unit', 'note']
        df = df[['category', 'number', 'village', 'address', 'longtitude', 'latitude', 'basement', 'capacity', 'unit', 'note']]
        df['city'] = f[27:30]
        df_all = pd.concat([df_all, df], ignore_index=True)
        # print(df_all['longtitude'])
    elif ',' in df[df.columns[4]][0]:
        df[['longtitude', 'latitude']] = df[df.columns[4]].str.split(',', n=1, expand = True)
        df.columns = ['category', 'number', 'village', 'address', '經緯度', 'basement', 'capacity', 'unit', 'note', 'longtitude', 'latitude']
        df['city'] = df['city'] = f[27:30]
        df = df[['category', 'number', 'village', 'address', 'longtitude', 'latitude', 'basement', 'capacity', 'unit', 'note', 'city']]
        df_all = pd.concat([df_all, df], ignore_index=True)
        # print(df.columns, len(df.columns), df)
    elif '，' in df[df.columns[4]][0]:
        df[['longtitude', 'latitude']] = df[df.columns[4]].str.split('，', n=1, expand = True)
        df.columns = ['category', 'number', 'village', 'address', '經緯度', 'basement', 'capacity', 'unit', 'note', 'longtitude', 'latitude']
        df['city'] = df['city'] = f[27:30]
        df = df[['category', 'number', 'village', 'address', 'longtitude', 'latitude', 'basement', 'capacity', 'unit', 'note', 'city']]
        df_all = pd.concat([df_all, df], ignore_index=True)
df_all = df_all.drop_duplicates()
df_all = df_all.drop_duplicates(subset=['address'])
df_all['latitude'] = df_all['latitude'].str.replace('O', '0')
# df_all.reset_index(inplace=True)
# print(df_all[df_all['latitude'].str.contains('120.81341020696392', regex=False, na=False)])
# print(df_all)
# print(df_all[df_all['number'].isnull()])
# print(df_all.iloc[0,10])
# for i in range(86718,len(df_all)):
#     print(i, df_all['latitude'][i])
#     df_all['latitude'][i] = float(df_all['latitude'][i])

df_all.to_sql('aircraft', engine, if_exists='append', index=False)
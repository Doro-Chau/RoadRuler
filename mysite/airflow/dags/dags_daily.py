from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta, datetime
import sys
sys.path.append('/home/ec2-user/Project_disaster_map/mysite/alertdata/')
from tasks import getConstruction, getParking, get_db_handle, getLiveVD, getCCTV

with DAG('daily_dag', start_date=datetime(2022, 7, 4), schedule_interval='@daily', catchup=False) as dag:
    get_construction = PythonOperator(
            task_id='get_construction',
            python_callable=getConstruction
            )
    get_CCTV = PythonOperator(
            task_id='get_CCTV',
            python_callable=getCCTV
            )


from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta, datetime 
import sys
sys.path.append('/home/ec2-user/Project_disaster_map/mysite/alertdata/')
from tasks import getParking, get_db_handle, getLiveVD
default_args = {
        'owner': 'dorothy',
        'start_date': datetime(2022, 7, 4),
        'email': ['chargespot4@gmail.com'],
        'email_on_failure': True,
        'email_on_retry': True,
        'retries': 1,
        'retry_delay': timedelta(minutes=1),}


with DAG('my_dag', start_date=datetime(2022, 7, 4), schedule_interval='* * * * *', catchup=False) as dag:
    get_parkinglot = PythonOperator(
            task_id='get_parkinglot',
            python_callable=getParking
            )
    get_road = PythonOperator(
            task_id='get_road',
            python_callable=getLiveVD
            )

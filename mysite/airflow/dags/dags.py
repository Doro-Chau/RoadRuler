from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta, datetime
import sys

sys.path.append("/home/ec2-user/Project_disaster_map/mysite/alertdata/")
from tasks import get_parking, get_db_handle, get_liveVD, store_realtime

default_args = {
    "owner": "dorothy",
    "start_date": datetime(2022, 7, 4),
    "email": ["chargespot4@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": True,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}


with DAG(
    "my_dag",
    start_date=datetime(2022, 7, 4),
    schedule_interval="*/2 * * * *",
    catchup=False,
) as dag:
    getparkinglot = PythonOperator(task_id="getparkinglot", python_callable=get_parking)
    gettraffic = PythonOperator(task_id="gettraffic", python_callable=get_liveVD)
    storerealtime = PythonOperator(
        task_id="storerealtime", python_callable=store_realtime
    )
    [getparkinglot, gettraffic] >> storerealtime

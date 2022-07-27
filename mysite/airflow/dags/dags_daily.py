from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import timedelta, datetime
import sys

sys.path.append("/home/ec2-user/Project_disaster_map/mysite/alertdata/")
from tasks import get_construction, get_db_handle, get_CCTV, store_daily

with DAG(
    "daily_dag",
    start_date=datetime(2022, 7, 4),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    getconstruction = PythonOperator(
        task_id="getconstruction", python_callable=get_construction
    )
    getCCTV = PythonOperator(task_id="getCCTV", python_callable=get_CCTV)
    storedaily = PythonOperator(task_id="storedaily", python_callable=store_daily)

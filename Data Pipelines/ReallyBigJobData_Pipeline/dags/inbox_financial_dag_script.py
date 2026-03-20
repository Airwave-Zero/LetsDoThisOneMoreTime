from airflow.sdk import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys
import logging
sys.path.append("/opt/airflow")

from gmail_related.BoA_Gmail_ETL import main as bank_gmail_etl

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG( 
    dag_id="bank_gmail_etl",
    start_date=datetime(2025, 7, 5),
    schedule="* * * * *",  # every 1 minute
    catchup=False,
    default_args=default_args,
)

t1 = PythonOperator(
    task_id="bank_gmail_etl",
    python_callable=bank_gmail_etl,
    dag=dag,
)

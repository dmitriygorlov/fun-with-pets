from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.email_operator import EmailOperator
from scripts.fetch_joke import fetch_and_store_joke, fetch_joke_from_db
import os

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

reception_email = os.environ.get("EMAIL_FOR_REPORT")

dag = DAG(
    "fetch_and_store_joke",
    default_args=default_args,
    description="Fetch joke from API, store in Postgresm retrieve and send via email",
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 10, 16),
    catchup=False,
)

fetch_store_joke_task = PythonOperator(
    task_id="fetch_and_store_joke",
    python_callable=fetch_and_store_joke,
    dag=dag,
)

fetch_joke_from_db_task = PythonOperator(
    task_id="fetch_joke_from_db",
    python_callable=fetch_joke_from_db,
    dag=dag,
)

send_email_task = EmailOperator(
    task_id="send_joke_email",
    to=reception_email,
    subject="Daily Joke",
    html_content="{{ task_instance.xcom_pull(task_ids='fetch_joke_from_db') }}",
    dag=dag,
)

fetch_store_joke_task >> fetch_joke_from_db_task >> send_email_task

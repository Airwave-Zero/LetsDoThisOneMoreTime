from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import sys

sys.path.append("/opt/airflow")

from Pokemon_TCG_Prices import TCG_Script_private

# Define card list inside the DAG file (or pass via variable in future)
card_names = [
    "Charizard", "Bulbasaur", "Gengar", "Umbreon", "Eevee",
    "Flygon", "Gardevoir", "Metagross", "Swampert", "Snorlax",
    "Arcanine", "Lucario", "Absol", "Blaziken", "Dragonite",
    "Greninja", "Mimikyu", "Garchomp", "Mudkip", "Sceptile",
    "Tyranitar", "Raichu", "Mew", "Ampharos", "Torterra"
]

def run_ebay_etl():
    track_price_history(card_names, folder_path="eBay_Card_Prices", max_results=200)

# DAG definition
with DAG(
    dag_id="ebay_etl_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:

    scrape_task = PythonOperator(
        task_id="ebay_etl_pipeline",
        python_callable=run_ebay_etl
    )

    scrape_task

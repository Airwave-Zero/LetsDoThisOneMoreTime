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

def dummy_test():
    print("Successfully imported TCG_Script_private")
    print(dir(TCG_Script_private))  # Shows available methods in the module

with DAG(
    dag_id="test_import_tcg_script",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    schedule_interval=None,
) as dag:
    t1 = PythonOperator(
        task_id="test_import",
        python_callable=dummy_test,
    )

    t1

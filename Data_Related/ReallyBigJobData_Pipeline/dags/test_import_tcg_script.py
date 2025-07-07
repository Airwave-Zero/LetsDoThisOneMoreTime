from airflow.sdk import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import sys
import logging
sys.path.append("/opt/airflow")

# Define card list inside the DAG file (or pass via variable in future)
card_names = [
    "Charizard", "Bulbasaur", "Gengar", "Umbreon", "Eevee",
    "Flygon", "Gardevoir", "Metagross", "Swampert", "Snorlax",
    "Arcanine", "Lucario", "Absol", "Blaziken", "Dragonite",
    "Greninja", "Mimikyu", "Garchomp", "Mudkip", "Sceptile",
    "Tyranitar", "Raichu", "Mew", "Ampharos", "Torterra"
]

def dummy_test():
    import logging
    import sys
    logging.info(f"sys.path: {sys.path}")

    try:
        logging.info("Trying import...")
        import Pokemon_TCG_Prices.dummy_import_test as dummy
        logging.info("Import worked!")
    except Exception as e:
        logging.error(f"Import failed: {e}")
        raise

    return "success"


default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG( 
    dag_id="test_import_tcg_script",
    start_date=datetime(2025, 7, 5),
    schedule="* * * * *",  # every 1 minute
    catchup=False,
    default_args=default_args,
)

t1 = PythonOperator(
    task_id="test_import",
    python_callable=dummy_test,
    dag=dag,
)

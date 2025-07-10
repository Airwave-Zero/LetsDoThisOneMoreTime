from airflow.sdk import DAG, task
from datetime import datetime, timedelta
import sys
import logging
import Pokemon_TCG_Prices.TCG_Script_private as tcg_script

if "/opt/airflow" not in sys.path:
    sys.path.append("/opt/airflow")

# Define card list inside the DAG file (or pass via variable in future)
card_names = [
    "Charizard", "Bulbasaur", "Gengar", "Umbreon", "Eevee",
    "Flygon", "Gardevoir", "Metagross", "Swampert", "Snorlax",
    "Arcanine", "Lucario", "Absol", "Blaziken", "Dragonite",
    "Greninja", "Mimikyu", "Garchomp", "Mudkip", "Sceptile",
    "Tyranitar", "Raichu", "Mew", "Ampharos", "Torterra"
]

# Define the DAG with SDK-style context manager
with DAG(
    dag_id="tcg_lookup_dag",
    start_date=datetime(2025, 7, 5),
    schedule="0 12 * * 0",  # Every Sunday at 12:00 PM
    catchup=False,
    default_args={
        "owner": "airflow",
        "retries": 1,
        "retry_delay": timedelta(minutes=1),
    },
) as dag:

    @task()
    def tcg_lookup():
        logging.info(f"sys.path: {sys.path}")
        try:
            tcg_script.lookup_tcg_price(card_names)
        except Exception as e:
            logging.error(f"Error: {e}")
            raise
        return "success"
    tcg_lookup()

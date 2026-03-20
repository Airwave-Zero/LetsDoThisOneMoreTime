from airflow.sdk import DAG, task
from datetime import datetime, timedelta
import sys
import logging
import Pokemon_TCG_Prices.eBay_Script as ebay_script

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
    dag_id="eBay_Pipeline_dag",
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
    def ebay_etl():
        logging.info(f"sys.path: {sys.path}")
        try:
            ebay_script.track_price_history(card_names, "eBay_Card_Prices", 200)
        except Exception as e:
            logging.error(f"Error: {e}")
            raise
        return "success"

    ebay_etl()

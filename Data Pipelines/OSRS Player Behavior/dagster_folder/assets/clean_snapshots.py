from dagster import asset
import clean_bronze_snapshots_parquet
from .get_snapshots import get_snapshots

@asset(deps=[get_snapshots])
def clean_snapshots():
    clean_bronze_snapshots_parquet.main()
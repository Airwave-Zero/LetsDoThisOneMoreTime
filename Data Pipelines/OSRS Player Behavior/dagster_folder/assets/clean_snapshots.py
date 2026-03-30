from dagster import asset
import clean_bronze_snapshots_parquet

@asset
def clean_snapshots():
    clean_bronze_snapshots_parquet.main()
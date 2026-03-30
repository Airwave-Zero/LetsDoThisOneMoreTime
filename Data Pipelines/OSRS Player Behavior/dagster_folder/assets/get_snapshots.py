from dagster import asset
import gather_raw_snapshots_bronze

@asset
def get_snapshots():
    gather_raw_snapshots_bronze.main()
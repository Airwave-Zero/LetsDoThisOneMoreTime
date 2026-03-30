from dagster import Definitions

from dagster_folder.assets.get_snapshots import get_snapshots
from dagster_folder.assets.clean_snapshots import clean_snapshots
#from dagster_folder.assets.generate_gold import build_gold

from dagster_folder.jobs.run_daily import daily_job
from dagster_folder.schedules.schedule_daily import daily_schedule

defs = Definitions(
    assets=[get_snapshots, clean_snapshots],
    jobs=[daily_job],
    schedules=[daily_schedule],
)
from dagster import ScheduleDefinition
from dagster_folder.jobs.run_daily import daily_job

# For PDT (Daylight Saving)
daily_schedule = ScheduleDefinition(
    job=daily_job,
    cron_schedule="0 1 * * *",  # 6 PM PDT daily
)
'''
# For standard PST
daily_schedule_pst = ScheduleDefinition(
    job=daily_job,
    cron_schedule="0 2 * * *",  # 6 PM PST daily
)
'''

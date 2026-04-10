from dagster import ScheduleDefinition
from dagster_folder.jobs.run_daily import daily_job

# For PDT (Daylight Saving)
daily_schedule = ScheduleDefinition(
    job=daily_job,
    cron_schedule="0 1 * * *",  # 1:00 AM PST (UTC+9 conversion)
    execution_timezone="America/Los_Angeles",  # Ensure the schedule runs in the correct timezone
)
'''
# For standard PST
daily_schedule_pst = ScheduleDefinition(
    job=daily_job,
    cron_schedule="0 2 * * *",  # 6 PM PST daily
    execution_timezone="America/Los_Angeles",  # Ensure the schedule runs in the correct timezone   
)
'''